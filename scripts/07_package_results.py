import _bootstrap
import argparse,json,zipfile
from pathlib import Path
from mrs.data import load_plan
from mrs.common import file_hash,write_json
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--allow-partial',action='store_true');a=p.parse_args()
root=Path(a.plan).resolve();out=Path(a.out).resolve();lock,rs,missing=load_plan(root,a.allow_partial)
if out.is_relative_to(root):raise SystemExit('Output ZIP must be outside the plan directory')
files=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='CHECKSUMS.json')
# Never place API keys or credential files in run plans. Explicit file allow-list excludes common credential files.
if any(p.name in ['.env','credentials.json'] or p.suffix in ['.key','.pem'] for p in files):raise SystemExit('Credential-like file found; remove it from export scope')
write_json(root/'CHECKSUMS.json',{str(p.relative_to(root)):file_hash(p) for p in files})
files.append(root/'CHECKSUMS.json');out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,root.name+'/'+str(f.relative_to(root)))
print(json.dumps({'zip':str(out),'sha256':file_hash(out),'completed':len(rs),'missing':len(missing),'purpose':lock['purpose']}))
