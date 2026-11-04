from pathlib import Path
import json
from .common import read_json,file_hash,digest

def load_plan(root,allow_partial=False):
 root=Path(root);lock=read_json(root/'protocol.lock.json')
 trials=[json.loads(x) for x in (root/'manifest.jsonl').read_text().splitlines()]
 if digest(trials)!=lock['manifest_hash']:raise ValueError('manifest integrity failure')
 results=[];missing=[]
 for t in trials:
  p=root/'runs'/t['trial_id'];d=p/'DONE.json'
  if not d.exists():missing.append(t['trial_id']);continue
  done=read_json(d)
  for name,h in done['hashes'].items():
   if file_hash(p/name)!=h:raise ValueError('raw result integrity failure: '+str(p/name))
  r=read_json(p/done['attempt']/'result.json')
  if r['trial']!=t or r['model_config']!=lock['model']:raise ValueError('trial/model mismatch')
  if not r['valid']:raise ValueError('invalid result')
  r['_path']=str(p/done['attempt']);results.append(r)
 if missing and not allow_partial:raise ValueError(f'{len(missing)} trials incomplete; finish or use explicit --allow-partial for exploratory reporting')
 return lock,results,missing
