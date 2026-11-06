"""Bounded contact-causality diagnostic on cached Qwen and Phi local models."""
from pathlib import Path
import modal,sys
if not modal.is_local():sys.path.insert(0,'/project/scripts')
from modal_qwen3 import image,evidence,weights
app=modal.App('workin-contact-causal')

@app.function(image=image,gpu='H100',cpu=8,memory=32768,volumes={'/evidence':evidence,'/hf':weights},timeout=7200,max_containers=4,retries=0)
def run(version:str='v1',scenario:str='B'):
    import datetime,hashlib,json,os,subprocess,time,urllib.request,zipfile
    from huggingface_hub import snapshot_download
    os.environ['CONTACT_SCENARIO']=scenario
    from contact_causal import MODELS
    os.chdir('/project')
    root=Path('/evidence')/('contact_causal_'+version+'_'+scenario);root.mkdir(exist_ok=False)
    server=None
    def note(s):
        with (root/'EXECUTION_LOG.md').open('a') as f:f.write('\n- '+datetime.datetime.now(datetime.timezone.utc).isoformat()+' '+s+'\n')
        print(s,flush=True);evidence.commit()
    def command(args,label):
        with (root/(label+'.log')).open('w') as f:
            p=subprocess.Popen([sys.executable,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            for line in p.stdout:
                f.write(line);f.flush();print(line,end='',flush=True);evidence.commit()
            rc=p.wait()
        if rc:raise RuntimeError(label+' failed')
    try:
        note('Authorized real-model contact diagnostic. One H100, 2-hour ceiling. No hosted OpenAI inference. Fixed development gate then fixed 24-scene cohort per model.')
        (root/'environment.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
        (root/'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True))
        with zipfile.ZipFile(root/'source.zip','w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
            for p in Path('/project').rglob('*'):
                if p.is_file() and '__pycache__' not in str(p):z.write(p,p.relative_to('/project'))
        for key,(model,revision) in MODELS.items():
            note('Starting '+key)
            snapshot_download(model,revision=revision,allow_patterns=['*.json','*.safetensors','*.jinja','*.txt','*.model']);weights.commit()
            handle=(root/(key+'_server.log')).open('w')
            server=subprocess.Popen([sys.executable,'-m','vllm.entrypoints.openai.api_server','--model',model,'--revision',revision,'--tokenizer-revision',revision,'--host','127.0.0.1','--port','8000','--dtype','bfloat16','--max-model-len','8192','--gpu-memory-utilization','.9','--max-num-seqs','16','--enforce-eager','--no-enable-prefix-caching','--seed','9217'],stdout=handle,stderr=subprocess.STDOUT)
            deadline=time.monotonic()+900
            while True:
                if server.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Server unavailable')
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8000/v1/models',timeout=5) as r:json.load(r)
                    break
                except OSError:time.sleep(3)
            os.environ['MRS_API_BASE']='http://127.0.0.1:8000/v1'
            try:
                command(['scripts/contact_causal.py','--out',str(root/(key+'_gate')),'--model',key,'--gate'],key+'_gate')
            except RuntimeError:
                note(key+' gate failed; main omitted')
                server.terminate();server.wait(timeout=30);server=None;handle.close();time.sleep(8)
                continue
            note(key+' clean gate passed')
            command(['scripts/contact_causal.py','--out',str(root/(key+'_main')),'--model',key],key+'_main')
            note(key+' cohort complete')
            server.terminate()
            try:server.wait(timeout=30)
            except subprocess.TimeoutExpired:server.kill();server.wait()
            server=None;handle.close();time.sleep(8)
        note('Completed both model cohorts')
    except BaseException as e:note('FAILED '+repr(e));raise
    finally:
        if server is not None:
            server.terminate()
            try:server.wait(timeout=30)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        files=sorted(p for p in root.rglob('*') if p.is_file())
        (root/'CHECKSUMS.json').write_text(json.dumps({p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
        with zipfile.ZipFile(root/(root.name+'.zip'),'w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
            for p in files+[root/'CHECKSUMS.json']:z.write(p,p.relative_to(root))
        evidence.commit()
    return str(root)

@app.local_entrypoint()
def main(version:str='v5'):
    for result in run.starmap([(version,s) for s in ('B','C_paused')],return_exceptions=True):
        print(result)
