"""Bounded Qwen3-8B development/discovery on Modal; no OpenAI service calls.

Authenticate via MODAL_TOKEN_ID / MODAL_TOKEN_SECRET or Modal's config.
Run: modal run --detach scripts/modal_qwen3.py --stage development
All evidence is committed to a named Volume after each completed trial.
"""
from pathlib import Path
import modal

MODEL = 'Qwen/Qwen3-8B'
REVISION = 'b968826d9c46dd6066d109eabc6255188de91218'
ROOT = Path(__file__).resolve().parents[1]
app = modal.App('workin-qwen3-memory-safety')
evidence = modal.Volume.from_name('workin-memory-safety-evidence', create_if_missing=True)
weights = modal.Volume.from_name('workin-qwen3-hf-cache', create_if_missing=True)
image = (
    modal.Image.from_registry('vllm/vllm-openai:v0.10.2')
    .entrypoint([])
    .apt_install('libgl1', 'libglib2.0-0')
    .run_commands('python3 --version', 'ln -s /usr/bin/python3 /usr/local/bin/python')
    .pip_install('scipy==1.17.0', 'matplotlib==3.10.8', 'Pillow==12.3.0',
                 'mujoco==3.17.0', 'imageio==2.38.1', 'imageio-ffmpeg==0.8.0', 'pytest==9.2.0')
    .env({'HF_HOME':'/hf', 'MUJOCO_GL':'egl', 'PYTHONPATH':'/project/src',
          'VLLM_USE_V1':'1', 'TOKENIZERS_PARALLELISM':'false'})
    .add_local_dir(ROOT / 'src', '/project/src')
    .add_local_dir(ROOT / 'scripts', '/project/scripts')
    .add_local_dir(ROOT / 'tests', '/project/tests')
    .add_local_dir(ROOT / 'configs', '/project/configs')
    .add_local_file(ROOT / 'pyproject.toml', '/project/pyproject.toml')
)


@app.function(image=image, gpu='A10G', cpu=4, memory=32768,
              volumes={'/evidence':evidence, '/hf':weights},
              timeout=7200, max_containers=1, retries=0)
def experiment(stage: str = 'development', version: str = 'v1'):
    import datetime, hashlib, importlib.metadata, json, os, shutil
    import subprocess, sys, time, urllib.request, zipfile
    if stage not in ('development', 'discovery'):
        raise ValueError('Only bounded E1/E2 cohorts are enabled.')
    if not version.replace('_','').isalnum():
        raise ValueError('Invalid version')
    os.chdir('/project')
    name = f'qwen3_8b_{stage}_{version}'
    root = Path('/evidence') / name
    root.mkdir(exist_ok=True)
    plan = root / 'plan'
    log = root / 'EXECUTION_LOG.md'
    def note(message):
        with log.open('a') as f:
            f.write(f'\n- {datetime.datetime.now(datetime.timezone.utc).isoformat()}: {message}\n')
        print(message, flush=True)
    def command(args, label):
        note('Running ' + label)
        with (root / f'{label}.log').open('a') as output:
            p = subprocess.Popen([sys.executable, *args], stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in p.stdout:
                output.write(line); output.flush(); print(line, end='', flush=True)
                if '"status": "completed"' in line:
                    evidence.commit()
            code = p.wait()
        evidence.commit()
        if code:
            raise RuntimeError(f'{label} exited {code}; logs preserved')
    server = None
    started = time.monotonic()
    try:
        note(f'Authorized bounded {stage}: 60 rollouts, one A10G, 2h function timeout, no retries; local date 2026-11-04 Asia/Karachi.')
        note(f'Model {MODEL}@{REVISION}; vLLM 0.10.2; non-thinking; temperature .7, top_p .8, top_k 20, per-request seeds.')
        (root / 'environment.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
        (root / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True))
        source = root / 'source.zip'
        if not source.exists():
            with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED) as z:
                for p in Path('/project').rglob('*'):
                    if p.is_file() and '__pycache__' not in str(p):z.write(p,p.relative_to('/project'))
        command(['-m','pytest','-q'], 'tests')
        command(['scripts/00_preflight.py'], 'physics_preflight')
        smoke = root / 'recovery_smoke'
        if not smoke.exists():
            command(['scripts/01_prepare.py','--stage','smoke','--suite','recovery','--n-seeds','1','--out',str(smoke)], 'smoke_prepare')
        command(['scripts/02_run.py','--plan',str(smoke),'--workers','2'], 'smoke_run')
        command(['scripts/03_validate.py','--plan',str(smoke)], 'smoke_validate')
        from huggingface_hub import snapshot_download
        note('Downloading pinned model weights.')
        snapshot_download(MODEL,revision=REVISION,allow_patterns=['*.json','*.safetensors','*.jinja','*.txt','*.model'])
        weights.commit()
        server_log = (root / 'vllm.log').open('a')
        server = subprocess.Popen([sys.executable,'-m','vllm.entrypoints.openai.api_server',
            '--model',MODEL,'--revision',REVISION,'--tokenizer-revision',REVISION,
            '--host','127.0.0.1','--port','8000','--dtype','bfloat16',
            '--max-model-len','4096','--gpu-memory-utilization','0.90',
            '--max-num-seqs','4','--enforce-eager','--seed','9217'],stdout=server_log,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+900
        while time.monotonic()<deadline:
            if server.poll() is not None:raise RuntimeError('vLLM exited; inspect vllm.log')
            try:
                with urllib.request.urlopen('http://127.0.0.1:8000/v1/models',timeout=5) as r:
                    models=json.load(r)
                assert MODEL in [m['id'] for m in models['data']]
                break
            except (OSError,AssertionError):time.sleep(5)
        else:raise RuntimeError('Model startup exceeded 15 minutes')
        os.environ['MRS_API_BASE']='http://127.0.0.1:8000/v1'
        os.environ.pop('MRS_API_KEY',None)
        command(['scripts/00_preflight.py','--check-endpoint'], 'model_preflight')
        if not plan.exists():
            command(['scripts/01_prepare.py','--stage',stage,'--provider','openai_compatible',
                '--model',MODEL,'--revision',REVISION,'--temperature','0.7','--top-p','0.8',
                '--top-k','20','--disable-thinking','--send-seed','--out',str(plan)], 'prepare')
        note('Frozen cohort prepared; beginning actual Qwen3 decisions.')
        evidence.commit()
        command(['scripts/02_run.py','--plan',str(plan),'--workers','2'], 'run')
        command(['scripts/03_validate.py','--plan',str(plan)], 'validate')
        command(['scripts/04_analyze.py','--plan',str(plan)], 'analyze')
        command(['scripts/05_video.py','--plan',str(plan),'--out',str(plan/'analysis'/'paired.mp4')], 'video')
        note(f'Completed and validated {stage}; elapsed wall seconds {time.monotonic()-started:.1f}. Monetary charges not estimated.')
        shutil.copy2(log,plan/'EXECUTION_LOG.md')
        command(['scripts/07_package_results.py','--plan',str(plan),'--out',str(root/f'{name}.zip')], 'package')
        return {'status':'complete','volume':'workin-memory-safety-evidence','directory':name}
    except BaseException as exc:
        note(f'FAILED: {type(exc).__name__}: {exc}; all existing evidence retained.')
        raise
    finally:
        if server is not None:
            server.terminate()
            try:server.wait(timeout=20)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        evidence.commit()


@app.local_entrypoint()
def main(stage: str = 'development', version: str = 'v1'):
    print(experiment.remote(stage, version))
