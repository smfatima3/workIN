import _bootstrap
import argparse,json,os,sys,urllib.request
from mrs.common import environment,code_hash
from mrs.world import World
p=argparse.ArgumentParser();p.add_argument('--check-endpoint',action='store_true');a=p.parse_args()
w=World(1);w.move({1:w.route(1,'detour'),2:w.route(2,'detour')},{1:.7,2:.7})
assert w.metrics()['task_success'] and not w.metrics()['violation'],w.metrics()
print(json.dumps({'status':'physics_preflight_pass','code_hash':code_hash(),'environment':environment()},indent=2))
if a.check_endpoint:
 base=os.environ['MRS_API_BASE'].rstrip('/'); headers={}
 if os.environ.get('MRS_API_KEY'): headers['Authorization']='Bearer '+os.environ['MRS_API_KEY']
 with urllib.request.urlopen(urllib.request.Request(base+'/models',headers=headers),timeout=30) as r:
  data=json.load(r)
 print(json.dumps({'available_models':[x['id'] for x in data.get('data',[])]}))
