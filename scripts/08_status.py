import _bootstrap
import argparse,json,time
from pathlib import Path
from mrs.common import read_json,write_json
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);a=p.parse_args();root=Path(a.plan)
trials=[json.loads(x) for x in (root/'manifest.jsonl').read_text().splitlines()];counts={'complete':0,'failed':0,'running_or_interrupted':0,'pending':0}
for t in trials:
 r=root/'runs'/t['trial_id'];key='complete' if (r/'DONE.json').exists() else 'running_or_interrupted' if (r/'RUNNING.json').exists() else 'failed' if (r/'FAILED.json').exists() else 'pending';counts[key]+=1
report={'counts':counts,'total':len(trials),'updated_unix':time.time()};write_json(root/'status.json',report);print(json.dumps(report,indent=2))
