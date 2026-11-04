import _bootstrap
import argparse,concurrent.futures,json,os,socket,time,traceback
from pathlib import Path
from mrs.common import read_json,write_json,digest,file_hash,code_hash,environment
from mrs.experiment import execute
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--workers',type=int,default=1)
p.add_argument('--shards',type=int,default=1);p.add_argument('--shard-index',type=int,default=0);p.add_argument('--limit',type=int)
p.add_argument('--retry-failed',action='store_true');p.add_argument('--retry-interrupted',action='store_true')
a=p.parse_args();root=Path(a.plan);lock=read_json(root/'protocol.lock.json')
trials=[json.loads(l) for l in (root/'manifest.jsonl').read_text().splitlines()]
if digest(trials)!=lock['manifest_hash']:raise SystemExit('Manifest changed. Create a new versioned plan.')
if code_hash()!=lock['code_hash']:raise SystemExit('Code/config changed. Create a new versioned plan; never mix revisions.')
if environment()['packages']!=lock['environment']['packages']:raise SystemExit('Dependency versions changed. Use the frozen environment or create a new plan.')
if a.workers<1 or a.shards<1 or not 0<=a.shard_index<a.shards:raise SystemExit('invalid worker/shard options')
selected=[t for i,t in enumerate(trials) if i%a.shards==a.shard_index]
if a.limit is not None:selected=selected[:a.limit]
(root/'runs').mkdir(exist_ok=True)
write_json(root/f'environment_shard{a.shard_index}.json',environment())
def job(t):
 path=root/'runs'/t['trial_id'];path.mkdir(exist_ok=True)
 if (path/'DONE.json').exists():
  done=read_json(path/'DONE.json')
  if all(file_hash(path/k)==v for k,v in done['hashes'].items()):return 'already_complete'
  raise RuntimeError('Completed run integrity failure: '+str(path))
 if (path/'FAILED.json').exists() and not a.retry_failed:return 'failed_preserved'
 running=path/'RUNNING.json'
 if running.exists():
  info=read_json(running)
  if not a.retry_interrupted:return 'in_progress_or_interrupted'
  if info['host']!=socket.gethostname():raise RuntimeError('Foreign-host lock: establish worker termination manually before removing lock.')
  try:os.kill(info['pid'],0)
  except ProcessLookupError:running.unlink()
  else:raise RuntimeError('Worker still alive; cannot reclaim trial')
 try:
  with running.open('x') as f:json.dump({'pid':os.getpid(),'host':socket.gethostname(),'started':time.time()},f)
 except FileExistsError:return 'claimed_elsewhere'
 attempt_num=len(list(path.glob('attempt_*')))+1;attempt=path/f'attempt_{attempt_num:03d}';attempt.mkdir()
 write_json(attempt/'trial.json',t)
 try:
  execute(t,lock['model'],attempt)
  hashes={str(p.relative_to(path)):file_hash(p) for p in attempt.iterdir() if p.is_file()}
  write_json(path/'DONE.json',{'attempt':attempt.name,'hashes':hashes,'completed_unix':time.time()})
  if (path/'FAILED.json').exists():(path/'FAILED.json').unlink()
  return 'completed'
 except Exception as e:
  # Preserve errors and partial logs. No conversion to "safe" or a scripted fallback.
  write_json(path/'FAILED.json',{'attempt':attempt.name,'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()})
  return 'failed'
 finally:
  if running.exists():running.unlink()
counts={};start=time.monotonic();last_checkpoint=start
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
 futures={pool.submit(job,t):t for t in selected}
 while futures:
  ready,_=concurrent.futures.wait(futures,timeout=30,return_when=concurrent.futures.FIRST_COMPLETED)
  for f in ready:
   t=futures.pop(f);status=f.result();counts[status]=counts.get(status,0)+1
   print(json.dumps({'trial':t['trial_id'],'status':status,'counts':counts}),flush=True)
  now=time.monotonic()
  # At least every 20 minutes and after every completion; private shard checkpoints avoid races.
  if ready or now-last_checkpoint>=1200:
   write_json(root/f'checkpoint_shard{a.shard_index}.json',{'counts':counts,'pending':len(futures),'elapsed_s':now-start,'updated_unix':time.time()});last_checkpoint=now
print(json.dumps({'status':'runner_finished','counts':counts,'elapsed_s':time.monotonic()-start}))
if counts.get('failed') or counts.get('failed_preserved'):raise SystemExit(2)
