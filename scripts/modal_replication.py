"""Bounded independent-family replication on self-hosted Phi-4."""
from pathlib import Path
import modal,sys
if not modal.is_local():sys.path.insert(0,'/project/scripts')
from modal_qwen3 import image,evidence,weights
app=modal.App('workin-phi4-independent-replication')
MODEL='microsoft/phi-4';REVISION='2db69c1c3e91a05d2c64a3185acfbaf36f744e25'

@app.function(image=image,gpu='H100',cpu=8,memory=32768,volumes={'/evidence':evidence,'/hf':weights},
              timeout=14400,max_containers=1,retries=0)
def run(stage: str,version: str,offset: int=0):
    import datetime,hashlib,json,os,subprocess,time,urllib.request,zipfile,tarfile,io
    from huggingface_hub import snapshot_download
    if stage not in ('gate','main','upstream'):raise ValueError(stage)
    if not version.replace('_','').isalnum():raise ValueError(version)
    os.chdir('/project');root=Path('/evidence')/f'replication_phi4_{stage}_{version}';root.mkdir(exist_ok=False)
    servers=[];handles=[]
    def note(s):
        with (root/'EXECUTION_LOG.md').open('a') as f:f.write(f'\n- {datetime.datetime.now(datetime.timezone.utc).isoformat()} {s}\n')
        print(s,flush=True)
    def command(args,label,cwd='/project'):
        note('Running '+label)
        with (root/(label+'.log')).open('w') as log:
            p=subprocess.Popen([sys.executable,*args],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            try:
                for line in p.stdout:
                    log.write(line);log.flush();print(line,end='',flush=True)
                    if '"completed"' in line:evidence.commit()
                rc=p.wait()
            finally:
                if p.poll() is None:p.terminate();p.wait(timeout=20)
        evidence.commit()
        if rc:raise RuntimeError(f'{label} exited {rc}')
    def serve(model,revision,port,fraction,embed=False):
        snapshot_download(model,revision=revision,allow_patterns=['*.json','*.safetensors','*.jinja','*.txt','*.model']);weights.commit()
        log=(root/f'server_{port}.log').open('w');handles.append(log)
        args=[sys.executable,'-m','vllm.entrypoints.openai.api_server','--model',model,'--revision',revision,
            '--tokenizer-revision',revision,'--host','127.0.0.1','--port',str(port),'--dtype','bfloat16','--max-model-len','8192',
            '--gpu-memory-utilization',str(fraction),'--max-num-seqs','16','--enforce-eager','--no-enable-prefix-caching','--seed','9217']
        if embed:args+=['--task','embed']
        server=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT);servers.append(server)
        deadline=time.monotonic()+1200
        while time.monotonic()<deadline:
            if server.poll() is not None:raise RuntimeError(f'Model server {port} startup failed')
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/v1/models',timeout=5) as r:json.load(r)
                return
            except OSError:time.sleep(5)
        raise RuntimeError('Server startup timed out')
    try:
        note(f'User-authorized independent replication; {stage}; one H100; four-hour cap; no hosted OpenAI model; no automatic retries.')
        (root/'environment.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
        (root/'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True))
        with zipfile.ZipFile(root/'source.zip','w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
            for p in Path('/project').rglob('*'):
                if p.is_file() and '__pycache__' not in str(p):z.write(p,p.relative_to('/project'))
        command(['-m','pytest','-q'],'tests')
        if stage=='upstream':
            runner='/tmp/maple-memrl/bin/python'
            command(['-m','venv','--without-pip','--system-site-packages','/tmp/maple-memrl'],'memrl_venv')
            command(['-m','pip','--python',runner,'install','--no-cache-dir','memoryos==1.0.0','chonkie==1.2.1','qdrant-client==1.15.1','mem0ai==1.0.1','mysql-connector-python==9.5.0','nltk==3.9.2','schedule','redis','pika','neo4j','modelscope==1.31.0'],'memrl_install')
            os.environ['MAPLE_RUNNER_PYTHON']=runner
            (root/'memrl_environment.txt').write_text(subprocess.check_output([runner,'-m','pip','freeze'],text=True))
        serve(MODEL,REVISION,8000,.75 if stage!='gate' else .9)
        os.environ['MRS_API_BASE']='http://127.0.0.1:8000/v1'
        if stage!='gate':
            from mrs.maple_adapter import UPSTREAM,EMBED_MODEL,EMBED_REVISION
            url=f'https://codeload.github.com/xiong-wenjun/MAPLE-Guard/tar.gz/{UPSTREAM}'
            raw=urllib.request.urlopen(url,timeout=120).read()
            with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:t.extractall('/tmp/maple',filter='data')
            upstream=next(Path('/tmp/maple').iterdir());os.environ['MAPLE_SOURCE']=str(upstream)
            (root/'upstream_provenance.json').write_text(json.dumps({'url':url,'commit':UPSTREAM,
                'archive_sha256':hashlib.sha256(raw).hexdigest(),'license':'No top-level license found; upstream source not redistributed in evidence',
                'core_sha256':hashlib.sha256((upstream/'maple_guard/maple_guard_core.py').read_bytes()).hexdigest()},indent=2))
            serve(EMBED_MODEL,EMBED_REVISION,8001,.12,True)
            os.environ['MRS_EMBED_BASE']='http://127.0.0.1:8001/v1'
        if stage=='upstream':command(['scripts/maple_upstream_smoke.py','--out',str(root/'run')],'upstream')
        else:
            command(['scripts/replication_run.py','--stage',stage,'--out',str(root/'run'),'--offset',str(offset)],stage)
        note('Completed stage '+stage)
    except BaseException as e:note(f'FAILED {type(e).__name__}: {e}');raise
    finally:
        for s in servers:
            s.terminate()
            try:s.wait(timeout=20)
            except subprocess.TimeoutExpired:s.kill();s.wait()
        for h in handles:h.close()
        files=sorted(p for p in root.rglob('*') if p.is_file())
        (root/'CHECKSUMS.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
        with zipfile.ZipFile(root/(root.name+'.zip'),'w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
            for p in [*files,root/'CHECKSUMS.json']:z.write(p,p.relative_to(root))
        evidence.commit()
    return {'status':'complete','path':str(root)}

@app.local_entrypoint()
def main(stage: str='gate',version: str='v1',offset: int=0):
    print(run.remote(stage,version,offset))
