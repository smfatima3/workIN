"""Small real-model upstream MMLU execution, with raw local HTTP audit."""
import _bootstrap
import argparse,hashlib,json,os,subprocess,sys,threading,urllib.request,urllib.error
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from mrs.common import write_json
from mrs.maple_adapter import EMBED_MODEL,UPSTREAM
from replication_run import MODEL,REVISION


def main(out):
    root=Path(out);root.mkdir(parents=True,exist_ok=False)
    url='https://datasets-server.huggingface.co/rows?dataset=cais%2Fmmlu&config=abstract_algebra&split=test&offset=0&length=20'
    raw=urllib.request.urlopen(url,timeout=120).read();(root/'dataset_response.json').write_bytes(raw)
    rows=json.loads(raw)['rows']
    with (root/'mmlu20.jsonl').open('w') as f:
        for x in rows:
            r=x['row'];f.write(json.dumps(dict(id='mmlu_abstract_algebra_'+str(x['row_idx']),question=r['question'],choices=r['choices'],answer='ABCD'[r['answer']]))+'\n')
    write_json(root/'protocol.json',dict(upstream_commit=UPSTREAM,model=MODEL,revision=REVISION,
        embedding=EMBED_MODEL,dataset_url=url,dataset_sha256=hashlib.sha256(raw).hexdigest(),tasks=20,
        agents=3,rounds=2,seed=42,methods=['no_defense_memrl','maple_guard'],
        scope='small upstream integration reproduction; changed backbone/embedding/cohort size; not paper-number replication',
        response_budget='strict; errors preserved; no hash/scripted fallback'))
    lock=threading.Lock();active={'method':None}
    class Proxy(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            payload=self.rfile.read(int(self.headers['Content-Length']))
            port=8001 if self.path.endswith('/embeddings') else 8000
            req=urllib.request.Request(f'http://127.0.0.1:{port}'+self.path,payload,{'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(req,timeout=240) as r:body=r.read();status=r.status
            except urllib.error.HTTPError as e:body=e.read();status=e.code
            except Exception as e:body=json.dumps({'error':str(e)}).encode();status=502
            with lock:
                with (root/'raw_http.jsonl').open('a') as log:log.write(json.dumps(dict(method=active['method'],path=self.path,request=json.loads(payload),status=status,response=json.loads(body)))+'\n')
            self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
    server=ThreadingHTTPServer(('127.0.0.1',8002),Proxy);threading.Thread(target=server.serve_forever,daemon=True).start()
    upstream=Path(os.environ['MAPLE_SOURCE']);env=os.environ.copy();env['PYTHONPATH']=str(upstream)
    # The upstream frame's declared local endpoints are explicitly overridden.
    failures=[]
    try:
        for method in ['no_defense_memrl','maple_guard']:
            active['method']=method
            args=[sys.executable,'-m','maple_guard.run_mmlu','--config',str(upstream/'configs/mmlu_star.yaml'),
                '--dataset',str(root/'mmlu20.jsonl'),'--out',str(root/(method+'.jsonl')),
                '--tasks','20','--agents','3','--rounds','2','--warmup-tasks','2',
                '--stream-builder','sequential','--activation-schedule','even','--malicious-activation-rate','.2',
                '--random-attacker-count','1','--target-agent-id','2','--method',method,'--seed','42',
                '--strict-comparison','--response-budget-policy','strict','--chat-max-tokens','512',
                '--lookahead-target-max-tokens','128','--no-enable-pattern-judge',
                '--chat-base-url','http://127.0.0.1:8002/v1','--chat-model',MODEL,
                '--embed-base-url','http://127.0.0.1:8002/v1','--embed-model',EMBED_MODEL,
                '--memory-store-dir',str(root/(method+'_memory'))]
            write_json(root/(method+'_command.json'),args)
            with (root/(method+'.log')).open('w') as log:
                rc=subprocess.call(args,cwd=upstream,env=env,stdout=log,stderr=subprocess.STDOUT)
            write_json(root/(method+'_status.json'),{'exit_code':rc})
            if rc:failures.append(method)
            print(json.dumps({'method':method,'exit_code':rc,'status':'completed' if rc==0 else 'failed'}),flush=True)
    finally:server.shutdown();server.server_close()
    if failures:raise RuntimeError('Upstream integration failed: '+','.join(failures))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();main(a.out)
