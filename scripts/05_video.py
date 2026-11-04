import _bootstrap
import argparse,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio.v2 as imageio
from mrs.data import load_plan
from mrs.common import write_json,file_hash
p=argparse.ArgumentParser(description='Paired trajectory replay from recorded MuJoCo states. No model reruns.')
p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--seconds',type=int,default=24)
p.add_argument('--block-id');p.add_argument('--task',type=int,default=0);p.add_argument('--conditions',default='A,B,F');a=p.parse_args()
if not 8<=a.seconds<=90:raise SystemExit('Use 8–90 seconds')
lock,results,missing=load_plan(a.plan,True);groups=defaultdict(dict)
for r in results:groups[r['trial']['block_id']][r['trial']['condition']]=r
conditions=a.conditions.split(',');eligible=sorted(k for k,v in groups.items() if all(c in v for c in conditions))
if not eligible:raise SystemExit('No complete matched block')
block=a.block_id or eligible[0]
if block not in eligible:raise SystemExit('Specified block lacks selected conditions')
rs=[groups[block][c] for c in conditions];traces=[];events=[]
for r in rs:
 tr=[json.loads(x) for x in (Path(r['_path'])/'trajectory.jsonl').read_text().splitlines()];tr=[x for x in tr if x['task']==a.task]
 if not tr:raise SystemExit('Task not available')
 traces.append(tr);events.append([json.loads(x) for x in (Path(r['_path'])/'events.jsonl').read_text().splitlines()])
W=480;H=496;fps=12;duration=max(tr[-1]['t'] for tr in traces)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14);bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
except OSError:font=ImageFont.load_default();bold=font
colors=['#9ca3af','#2b77a0','#8d5ca6','#d18d31','#4e9c70']
def xy(p,offset):return (offset+int((p[0]+3.3)/6.6*W),int(142+(2.7-p[1])/5.4*260))
fixture=any(r['fixture'] for r in rs);out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
writer=imageio.get_writer(str(out),fps=fps,codec='libx264',quality=8,macro_block_size=8)
poster=None
for frame in range(a.seconds*fps):
 t=duration*frame/max(1,a.seconds*fps-1);im=Image.new('RGB',(W*len(rs),H),'#f8fafc');d=ImageDraw.Draw(im)
 for col,(r,tr,ev,c) in enumerate(zip(rs,traces,events,conditions)):
  off=W*col;state=tr[max(0,np.searchsorted([x['t'] for x in tr],t,side='right')-1)]
  label={'A':'A | Clean memory','B':'B | Source removed only','F':'F | Verify on use',
         'lineage_revoke_poison':'Lineage deletion','full_reset_poison':'Full reset','local_shield_poison':'Local shield'}.get(c,c)
  d.text((off+16,12),label,font=bold,fill='#163445')
  d.text((off+16,42),f"Seed {r['trial']['seed']} | {r['trial']['scenario']} | task {a.task+1}",font=font,fill='#334155')
  d.text((off+16,65),f'Elapsed simulation: {min(t,tr[-1]["t"]):.1f} s',font=font,fill='#334155')
  tag='SCRIPTED TEST — NOT RESEARCH RESULTS' if fixture else 'RECORDED PHYSICS TRAJECTORY REPLAY'
  d.text((off+16,88),tag,font=font,fill='#a33b32' if fixture else '#334155')
  d.text((off+16,112),f"Lineage p={r['trial'].get('provenance_coverage',1.)} | reads={r['trial'].get('inspection_budget','unlimited')} | failed sensor={r['trial']['sensor_fail']}",font=font,fill='#334155')
  x0,y0=xy((-.8,1.2),off);x1,y1=xy((.8,-1.2),off)
  d.rectangle([x0,y0,x1,y1],fill='#fbe8df' if r['trial']['restricted'] else '#dfeee3',outline='#cc8b72')
  d.text((x0+4,y0+6),'zone',font=font,fill='#733f31');ox,oy=xy((0,0),off);d.ellipse([ox-12,oy-12,ox+12,oy+12],fill='#64748b')
  for i,p2 in enumerate(state['xy']):
   path=[xy(x['xy'][i],off) for x in tr if x['t']<=t]
   if len(path)>1:d.line(path,fill=colors[i%len(colors)],width=2)
   x,y=xy(p2,off);d.ellipse([x-13,y-13,x+13,y+13],fill=colors[i%len(colors)]);d.text((x-5,y-8),str(i),font=font,fill='white')
  violated=any(state['violation']);d.text((off+16,414),'Executed violation: '+('YES' if violated else 'NO SO FAR'),font=bold,fill='#af3e30' if violated else '#276c58')
  writes=sum(x['kind']=='write' for x in ev);d.text((off+16,444),f'Memory writes: {writes} | source removed before task',font=font,fill='#334155')
  d.text((off+16,467),'0 source / 1 relay / 2+ receiver robots',font=font,fill='#334155')
  if col:d.line([off,0,off,H],fill='#b7c5ce',width=2)
 writer.append_data(np.asarray(im))
 if frame==a.seconds*fps//2:poster=im.copy()
writer.close()
if poster:poster.save(out.with_suffix('.png'))
manifest={'block_id':block,'selection':'lexicographically_first_complete_block' if not a.block_id else 'explicit_block_disclosed',
 'conditions':conditions,'trial_ids':[r['trial']['trial_id'] for r in rs],'fixture':fixture,'task':a.task,'seconds':a.seconds,
 'simulation_duration_s':duration,'alignment':'shared simulation clock; completed runs hold final frame',
 'rendering':'2D replay of recorded MuJoCo positions, not camera imagery','source_sha256':{r['trial']['trial_id']:file_hash(Path(r['_path'])/'trajectory.jsonl') for r in rs},'video_sha256':file_hash(out)}
write_json(out.with_suffix('.json'),manifest)
print(json.dumps({'video':str(out.resolve()),'fixture':fixture,'block_id':block},indent=2))
