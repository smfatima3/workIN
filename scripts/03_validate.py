import _bootstrap
import argparse,json
from pathlib import Path
from mrs.data import load_plan
from mrs.common import write_json
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--allow-partial',action='store_true');a=p.parse_args()
lock,results,missing=load_plan(a.plan,a.allow_partial)
issues=[];physical_states={}
for r in results:
 events=[json.loads(x) for x in (Path(r['_path'])/'events.jsonl').read_text().splitlines()]
 resets=[x for x in events if x['kind']=='reset']
 if len(resets)!=2:issues.append([r['trial']['trial_id'],'missing reset'])
 for reset in resets:
  if reset['transient_context'] or reset['queues'] or not reset['source_removed']:issues.append([r['trial']['trial_id'],'reset contamination'])
  if any(x['kind']=='zone' for x in reset['memories'][0]['items']):issues.append([r['trial']['trial_id'],'source not removed'])
  if not r['trial']['setting']['persistent'] and any(x['kind']=='zone' for s in reset['memories'] for x in s['items']):issues.append([r['trial']['trial_id'],'transient memory survived'])
 for e in events:
  if e['kind']=='physical_initialization':
   key=(r['trial']['block_id'],e['task_offset'])
   if key in physical_states and physical_states[key]!=e['state_hash']:issues.append([r['trial']['trial_id'],'unmatched physical initialization'])
   physical_states[key]=e['state_hash']
  if e['kind']=='model_call':
   text=json.dumps(e['prompt'])
   if 'evaluator_' in text or 'asserts_false' in text:issues.append([r['trial']['trial_id'],'evaluator label leak'])
 if r['fixture'] and lock['purpose']!='software_validation_only':issues.append([r['trial']['trial_id'],'fixture in research'])
 if lock.get('schema_version',1)>=2:
  if sum(e['kind']=='physical_initialization' for e in events)!=r['trial']['horizon']:issues.append([r['trial']['trial_id'],'missing physical checkpoint hash'])
  budget=r['trial'].get('inspection_budget')
  if budget is not None and r['inspection_budget_used']>budget*(r['trial']['n_robots']-1):issues.append([r['trial']['trial_id'],'observation budget exceeded'])
  if r['inspection_count']!=r['inspection_budget_used']:issues.append([r['trial']['trial_id'],'observation cost mismatch'])
report={'status':'PASS' if not issues and not missing else 'PARTIAL' if not issues else 'FAIL','completed':len(results),'missing':missing,'issues':issues,'fixture':any(r['fixture'] for r in results)}
write_json(Path(a.plan)/'validation.json',report);print(json.dumps(report,indent=2))
if issues:raise SystemExit(2)
