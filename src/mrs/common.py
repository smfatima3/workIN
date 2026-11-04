from pathlib import Path
import hashlib, json, os, time, platform, importlib.metadata
ROOT = Path(__file__).resolve().parents[2]

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',',':'), allow_nan=False).encode()).hexdigest()

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def code_hash():
    files = [p for folder in ['src','scripts','configs'] for p in (ROOT/folder).rglob('*')
             if p.is_file() and '__pycache__' not in str(p) and p.suffix in ['.py','.json','.xml']]
    return digest({str(p.relative_to(ROOT)):file_hash(p) for p in sorted(files)})

def write_json(path, obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w') as f:
        json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def read_json(path):
    return json.loads(Path(path).read_text())

def environment():
    versions={}
    for p in ['numpy','scipy','mujoco','matplotlib','Pillow','imageio','imageio-ffmpeg']:
        try: versions[p]=importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError: versions[p]=None
    return {'python':platform.python_version(),'platform':platform.platform(),'packages':versions}

class Log:
    def __init__(self,path):
        self.path=Path(path); self.count=0; self.lines=[]
        self.partial=self.path.with_name(self.path.name+'.partial')
    def add(self,kind,**kwargs):
        self.count+=1
        event={'event_id':self.count,'kind':kind,**kwargs}
        self.lines.append(json.dumps(event,sort_keys=True,allow_nan=False)+'\n')
        # Mutable progress is distinct from the immutable final evidence file.
        temp=self.partial.with_name(self.partial.name+'.tmp')
        with temp.open('w') as f:
            f.writelines(self.lines); f.flush(); os.fsync(f.fileno())
        os.replace(temp,self.partial)
        return event
    def finalize(self):
        if self.path.exists():raise RuntimeError('Refusing to overwrite finalized event evidence')
        temp=self.path.with_name(self.path.name+'.tmp')
        with temp.open('w') as f:
            f.writelines(self.lines); f.flush(); os.fsync(f.fileno())
        os.replace(temp,self.path)
        if self.partial.exists():self.partial.unlink()
