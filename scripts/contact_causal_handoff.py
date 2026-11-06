from pathlib import Path
import sys,json,csv,math,collections,argparse
parser=argparse.ArgumentParser()
parser.add_argument("--raw-root",required=True)
parser.add_argument("--out",required=True)
args=parser.parse_args()
REPO=Path(__file__).resolve().parents[1]
import numpy as np
import imageio.v2 as imageio
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(REPO/'src'))
from mrs.common import digest
sys.path.insert(0,str(REPO/'scripts'))
import contact_causal
from contact_manipulation import configure
REPLAY_CACHE={}
replay_audits=[]
OUT=Path(args.out);OUT.mkdir(parents=True,exist_ok=True)
SCENARIOS=['A','B','C_moving','C_paused'];ARMS=['retained','corrected','irrelevant','clean','blocked']
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
all_results=[]
rows=[];contrasts=[];audit=[];mechanism=[];usage=collections.Counter();gates=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for scenario in SCENARIOS:
 for model in ('qwen','phi'):
  version='v6' if scenario=='A' and model=='phi' else 'v7' if scenario=='C_moving' and model=='phi' else 'v5' if scenario in ('B','C_paused') else 'v4'
  root=Path(args.raw_root)/(f'contact_{version}_'+scenario)
  gate=root/(model+'_gate')/'gate.json'
  gates.append({'model':model,'scenario':scenario,'gate':read(gate) if gate.exists() else {'passed':False,'missing':True}})
  data=root/(model+'_main')
  if not data.exists():continue
  manifest=read(data/'manifest.json');results=[]
  for spec in manifest['scenes']:
   folder=data/'blocks'/spec['id'];cpp=folder/'checkpoints.json'
   if not cpp.exists():continue
   cps=read(cpp)
   for condition,cp in cps.items():
    expected=cp.pop('hash');assert digest(cp)==expected;cp['hash']=expected
    assert cp['source_disconnected'] and cp['queues']==[] and cp['sessions']==[]
   truth='occupied' if abs(spec['y'])<.2 else 'empty'
   mechanism.append({'model':model,'scenario':scenario,'scene':spec['id'],'receiver_false_retained':any(r['belief'] not in (truth,'unknown') for r in cps['false']['memory'])})
   for arm in ARMS:
    for rep in (0,1):
     p=folder/f'{arm}_r{rep}'
     if not (p/'result.json').exists():continue
     r=read(p/'result.json');trace=read(p/'trajectory.json');cp=cps['clean' if arm=='clean' else 'blocked' if arm=='blocked' else 'false']
     assert r['checkpoint_hash']==cp['hash']
     original_hash_match=r['initial_state_hash']==digest(cp['physical_state'])
     if scenario=='B':assert original_hash_match
     key=(scenario,json.dumps(spec,sort_keys=True),r['action'])
     if key not in REPLAY_CACHE:
      simulator=contact_causal.scene if scenario=='B' else configure(scenario,None)[0]
      REPLAY_CACHE[key]=simulator(spec,r['action'])
     replay=REPLAY_CACHE[key]
     assert replay['contact']==r['contact'] and replay['task_success']==r['task_success']
     assert len(replay['contacts'])==len(trace['contacts'])
     assert np.allclose([f['position_m'] for f in replay['frames']],[f['position_m'] for f in trace['frames']],rtol=0,atol=1e-6)
     assert np.allclose([c['normal_force_n'] for c in replay['contacts']],[c['normal_force_n'] for c in trace['contacts']],rtol=1e-6,atol=1e-5)
     assert np.allclose([c['time_s'] for c in replay['contacts']],[c['time_s'] for c in trace['contacts']],rtol=0,atol=1e-9)
     replay_audits.append({'model':model,'scenario':scenario,'scene':spec['id'],'arm':arm,'replicate':rep,'original_hash_match':original_hash_match,'sequential_replay_match':True,'reconstructed_initial_hash':replay['initial_state_hash']})
     assert r['contact']==bool(trace['contacts'])
     assert all(set(e['geoms'] if 'geoms' in e else [e['geom1'],e['geom2']]) in ({'base','person'},{'moving','person'}) and e['normal_force_n']>0 for e in trace['contacts'])
     r.update(model=model,scenario=scenario,scene_id=spec['id']);results.append(r)
  for p in data.rglob('events.jsonl'):
   for line in p.read_text().splitlines():
    e=json.loads(line)
    if e['kind']=='model_call':
     assert len(e['request']['messages'])==2
     u=e['raw_response'].get('usage',{});usage['calls']+=1;usage['input_tokens']+=u.get('prompt_tokens',0);usage['output_tokens']+=u.get('completion_tokens',0)
  all_results.extend(results)
  for arm in ARMS:
   rs=[r for r in results if r['arm']==arm];n=len(rs);intended=len(manifest['scenes'])*2;k=sum(r['contact'] for r in rs)
   rows.append({'model':model,'scenario':scenario,'arm':arm,'complete':n,'intended':intended,'contacts':k,'unknown':intended-n,'successes':sum(r['task_success'] for r in rs),'inspections':sum(r['inspection_reads'] for r in rs),'false_retained':sum(r['naturally_retained_false'] for r in rs),'edits_changed':sum(r['edit_changed'] for r in rs),'contact_bounds':[k/intended,(k+intended-n)/intended]})
  for left,right in [('retained','corrected'),('corrected','irrelevant'),('retained','clean'),('retained','blocked')]:
   diffs=[]
   for spec in manifest['scenes']:
    by={(r['arm'],r['replicate']):r['contact'] for r in results if r['scene_id']==spec['id']}
    if all((a,rep) in by for a in (left,right) for rep in (0,1)):
     diffs.append(np.mean([by[left,rep]-by[right,rep] for rep in (0,1)]))
   if diffs:
    d=float(np.mean(diffs));rng=np.random.default_rng(20261106);boot=np.mean(rng.choice(diffs,(10000,len(diffs))),axis=1);w=math.sqrt(2*math.log(2/(.05/32))/len(diffs))
    contrasts.append({'model':model,'scenario':scenario,'contrast':left+' minus '+right,'scene_pairs':len(diffs),'difference':d,'bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),'familywise_bounded_interval':[max(-1,d-w),min(1,d+w)]})
  audit.append({'model':model,'scenario':scenario,'complete':len(results),'intended':manifest['intended_continuations'],'validation':'PASS','failed_records':len(list(data.rglob('FAILED.json')))})
  if (OUT/f'{model}_{scenario}.mp4').exists():continue
  # The replay selection was fixed before main outcomes.
  parent=data/'blocks'/manifest['replay_scene'];panels=[]
  for arm in ARMS:
   p=parent/(arm+'_r0')
   panels.append((arm,read(p/'trajectory.json'),read(p/'result.json'),json.loads((p/'events.jsonl').read_text().splitlines()[0]))) if (p/'result.json').exists() else panels.append((arm,None,None,None))
  with imageio.get_writer(OUT/f'{model}_{scenario}.mp4',fps=12,codec='libx264',quality=7) as writer:
   for f in range(96):
    im=Image.new('RGB',(1536,768),'#f4f6f8');d=ImageDraw.Draw(im)
    d.text((20,12),f'{model.upper()} / {scenario} / {manifest["replay_scene"]} / replicate 0 / source disconnected',font=font,fill='#173449')
    for i,(arm,tr,r,event) in enumerate(panels):
     left=12+(i%3)*512;top=48+(i//3)*346
     d.rectangle((left,top,left+500,top+330),fill='white',outline='#c6d2d9');d.text((left+12,top+8),arm,font=font,fill='#173449')
     if tr is None:d.text((left+12,top+50),'Missing outcome',font=font,fill='red');continue
     v=tr['frames'][round(f*(len(tr['frames'])-1)/95)];x,y,z=v['position_m'];spec=r['scene']
     d.text((left+12,top+36),f'Command {r["action"]} / inspection reads {r["inspection_reads"]}',font=small,fill='#173449')
     beliefs=[x['belief'] for x in event['after'] if x['id']!='executor:notice']
     d.text((left+12,top+60),f'Memory {beliefs or "empty"}; correction changed {r["edit_changed"]}',font=small,fill='#173449')
     if scenario=='B':
      point=lambda a,b:(left+250+a*270,top+220-b*190)
      px,py=point(spec['x'],spec['y']);cx,cy=point(x,y)
      d.ellipse((px-27,py-19,px+27,py+19),fill='#d56d58' if v['contact_so_far'] else '#679ca0')
      d.rectangle((cx-25.65,cy-14.25,cx+25.65,cy+14.25),fill='#a46127')
     else:
      point=lambda a,b:(left+220+a*240,top+255-b*125)
      px=(.34 if scenario=='A' else 0)+spec['x']
      d.line((*point(-.85,0),*point(.9,0)),fill='#a5b3bd',width=2)
      if scenario=='A':d.rectangle((*point(-.82,.84),*point(.14,.76)),fill='#98aab1')
      d.rounded_rectangle((*point(px-.1,.51),*point(px+.1,.01)),radius=12,fill='#d56d58' if v['contact_so_far'] else '#679ca0')
      d.rectangle((*point(x-.095,z+.065),*point(x+.095,z-.065)),fill='#a46127')
     d.text((left+12,top+274),f't={v["time_s"]:.3f}s / contact recorded {v["contact_so_far"]}',font=small,fill='#173449')
     d.text((left+12,top+301),f'Final task success {r["task_success"]} / contact {r["contact"]}',font=small,fill='#173449')
    d.text((1050,460),'Real-model decisions / MuJoCo primitives',font=font,fill='#173449')
    d.text((1050,495),'Matched physical start / ideal inspection',font=small,fill='#173449')
    d.text((1050,525),'Schematic position replay / rotation omitted',font=small,fill='#173449')
    d.text((1050,555),'8 seconds shows 1.90 simulated seconds',font=small,fill='#173449')
    writer.append_data(np.asarray(im))
    if f==78:im.save(OUT/f'{model}_{scenario}.png')
for name,obj in [('trial_outcomes',all_results),('summary',rows),('contrasts',contrasts),('audit',audit),('mechanism',mechanism),('usage',dict(usage)),('gates',gates),('sequential_replay_audit',replay_audits)]:
 (OUT/(name+'.json')).write_text(json.dumps(obj,indent=2))
with (OUT/'results.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(json.dumps({'audit':audit,'usage':dict(usage)}))
