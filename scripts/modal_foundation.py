"""Explicit bounded launches for F1, F2/F3 and F4/F5/F6; no automatic tuning."""
from pathlib import Path
import modal
import sys
if not modal.is_local():sys.path.insert(0,'/project/scripts')
from modal_qwen3 import image,evidence,weights,MODEL,REVISION
app=modal.App('workin-foundation-f1-f6')

@app.function(image=image,gpu='H100',cpu=8,memory=32768,
              volumes={'/evidence':evidence,'/hf':weights},timeout=14400,max_containers=1,retries=0)
def run(stage: str,version: str,configuration: str='explicit',development_offset: int=0,resume_from: str=''):
    import datetime,json,os,subprocess,sys,time,urllib.request,zipfile,hashlib
    if stage not in ('f1','f23','f456'):raise ValueError(stage)
    if not version.replace('_','').isalnum():raise ValueError(version)
    os.chdir('/project')
    root=Path('/evidence')/f'foundation_{stage}_{version}'
    root.mkdir(exist_ok=False)
    if resume_from:
        import shutil
        if '/' in resume_from or '\\' in resume_from:raise ValueError('Expected evidence directory name')
        original=Path('/evidence')/resume_from
        frozen=Path('/tmp')/('frozen_'+version)
        frozen.mkdir(exist_ok=False)
        with zipfile.ZipFile(original/'source.zip') as z:z.extractall(frozen)
        shutil.copytree(original/'data',root/'data')
        shutil.copy2(original/'source.zip',root/'source.zip')
        shutil.copy2('/project/scripts/foundation_resume.py',root/'resume_harness.py')
        os.chdir(frozen)
    def note(s):
        with (root/'EXECUTION_LOG.md').open('a') as f:f.write(f'\n- {datetime.datetime.now(datetime.timezone.utc).isoformat()} {s}\n')
        print(s,flush=True)
    def command(args,label):
        note('Running '+label)
        with (root/f'{label}.log').open('w') as log:
            p=subprocess.Popen([sys.executable,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            for line in p.stdout:
                log.write(line);log.flush();print(line,end='',flush=True)
                if '"completed"' in line:evidence.commit()
            rc=p.wait()
        evidence.commit()
        if rc:raise RuntimeError(f'{label} exited {rc}')
    server=None;start=time.monotonic()
    try:
        note(f'User authorized F1--F6; stage={stage}, configuration={configuration}; one H100, hard timeout 4h, no automatic retries. F1 configuration selection was performed on A10; GPU details are retained.')
        (root/'environment.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
        (root/'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True))
        if not resume_from:
            with zipfile.ZipFile(root/'source.zip','w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
                for p in Path('/project').rglob('*'):
                    if p.is_file() and '__pycache__' not in str(p):z.write(p,p.relative_to('/project'))
        else:note('Resuming frozen source and original manifest from '+resume_from+'; interrupted attempts preserved, completed branches reused.')
        command(['-m','pytest','-q'],'tests')
        command(['scripts/00_preflight.py'],'preflight')
        from huggingface_hub import snapshot_download
        snapshot_download(MODEL,revision=REVISION,allow_patterns=['*.json','*.safetensors','*.jinja','*.txt','*.model']);weights.commit()
        with (root/'vllm.log').open('w') as slog:
            server=subprocess.Popen([sys.executable,'-m','vllm.entrypoints.openai.api_server','--model',MODEL,
                '--revision',REVISION,'--tokenizer-revision',REVISION,'--host','127.0.0.1','--port','8000',
                '--dtype','bfloat16','--max-model-len','8192','--gpu-memory-utilization','0.9',
                '--max-num-seqs','32' if stage=='f456' and not resume_from else '16','--enforce-eager','--no-enable-prefix-caching','--seed','9217'],stdout=slog,stderr=subprocess.STDOUT)
            deadline=time.monotonic()+900
            while time.monotonic()<deadline:
                if server.poll() is not None:raise RuntimeError('vLLM startup failed')
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8000/v1/models',timeout=5) as r:data=json.load(r)
                    assert MODEL in [x['id'] for x in data['data']];break
                except (OSError,AssertionError):time.sleep(5)
            else:raise RuntimeError('vLLM startup timeout')
            os.environ['MRS_API_BASE']='http://127.0.0.1:8000/v1'
            args=['scripts/foundation_f1.py','--out',str(root/'data')] if stage=='f1' else [
                'scripts/foundation_run.py','--stage',stage,'--configuration',configuration,'--out',str(root/'data')]
            if stage=='f23':args+=['--development-offset',str(development_offset)]
            if resume_from:args=['/project/scripts/foundation_resume.py','--source',str(frozen),'--root',str(root/'data')]
            command(args,stage)
        note(f'Completed {stage}; monotonic elapsed {time.monotonic()-start:.3f}s; charges not estimated.')
    except BaseException as e:
        note(f'FAILED {type(e).__name__}: {e}');raise
    finally:
        if server is not None:
            server.terminate()
            try:server.wait(timeout=20)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        files=sorted(p for p in root.rglob('*') if p.is_file())
        (root/'CHECKSUMS.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
        with zipfile.ZipFile(root/f'{root.name}.zip','w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
            for p in [*files,root/'CHECKSUMS.json']:z.write(p,p.relative_to(root))
        evidence.commit()
    return {'status':'complete','path':str(root)}

@app.local_entrypoint()
def main(stage: str='f1',version: str='v1',configuration: str='explicit',development_offset: int=0,resume_from: str=''):
    print(run.remote(stage,version,configuration,development_offset,resume_from))
