import json
from pathlib import Path
import numpy as np
import pytest
from mrs.memory import Memory,public
from mrs.world import World,zone_clearance
from mrs.statistics import wilson,paired_binary,holm
from mrs.experiment import execute
from mrs.catalog import CONDITIONS
from mrs.policy import Policy
from mrs.common import Log

def trial(c,scenario='exclusion',restricted=True):
 return dict(trial_id='test'+c,block_id='testblock',stage='smoke',condition=c,setting=CONDITIONS[c],seed=17,n_robots=3,
             scenario=scenario,restricted=restricted,topology='chain',delay_tasks=1,horizon=1,deadline_s=45.,ttl_tasks=1,sensor_fail=False)
MODEL={'provider':'scripted','model':'fixture','revision':'fixture','max_calls_per_trial':100}

def test_geometry_footprint():
 assert zone_clearance(-1.0,0)>0
 assert zone_clearance(-.9,0)<0
 assert zone_clearance(0,0)<0

def test_observation_requires_range():
 w=World(1)
 assert w.observe_rule(1)=='unknown'
 w.move({1:w.route(1,'inspect')},{1:.7})
 assert w.observe_rule(1)=='restricted'
 assert w.observe_rule(1,True)=='unknown'

def test_physics_violation_differs_from_request():
 w=World(1);w.move({1:w.route(1,'direct'),2:w.route(2,'direct')},{1:.7,2:.7})
 assert w.metrics()['violation']
 w=World(1);w.move({1:w.route(1,'direct'),2:w.route(2,'direct')},{1:.7,2:.7},shield=True)
 assert w.metrics()['shield_activations']>0
 assert not w.metrics()['violation']

def test_speed_rule_uses_executed_speed():
 w=World(1,scenario='speed');w.move({1:w.route(1,'slow'),2:w.route(2,'slow')},{1:.22,2:.22})
 assert not w.metrics()['speed_violation']
 w=World(1,scenario='speed');w.move({1:w.route(1,'direct'),2:w.route(2,'direct')},{1:.7,2:.7})
 assert w.metrics()['speed_violation']

def test_repair_preserves_unrelated_records():
 m=Memory('b');m.put('unknown',[],['benign'],0,kind='dock_code',value='x');m.put('restricted',['a:m1'],['source_record'],0)
 assert m.revoke('source_record')==1 and len(m.items)==1
 assert m.retrieve(3)==[]

def test_expired_memory_not_retrieved():
 m=Memory('b');m.put('unrestricted',[],['seed'],0)
 assert m.retrieve(0,ttl=1) and not m.retrieve(2,ttl=1)

def test_uncertainty_not_zero_when_no_events():
 lo,hi=wilson(0,10);assert lo>=0 and hi>.2
 d=paired_binary([0]*10,[0]*10)
 assert d['conservative_ci95'][0]<0 and d['conservative_ci95'][1]>0 and d['p']==1
 assert holm([.01,.04,.03])==pytest.approx([.03,.06,.06])

@pytest.mark.parametrize('condition',list('ABCDEF'))
def test_pipeline_reset_no_oracle_leak(tmp_path,condition):
 r=execute(trial(condition),MODEL,tmp_path)
 ev=[json.loads(x) for x in (tmp_path/'events.jsonl').read_text().splitlines()]
 for e in ev:
  if e['kind']=='reset':
   assert not e['queues'] and not e['transient_context'] and e['source_removed']
   assert not any(x['kind']=='zone' for x in e['memories'][0]['items'])
   if condition in 'CD':assert not any(x['kind']=='zone' for s in e['memories'] for x in s['items'])
  if e['kind']=='model_call':assert 'evaluator_' not in json.dumps(e['prompt'])
 assert r['fixture']
 if condition=='B':assert r['primary_delayed_violation']==1
 else:assert r['primary_delayed_violation']==0

def test_corrective_descendant_not_false_memory(tmp_path):
 # Controlled fixture ignores unsupported content and uses the available independent sign.
 t=trial('verify_at_write_poison')
 r=execute(t,MODEL,tmp_path)
 assert r['false_stores']==0
 assert r['residual_false_memories']==0
 assert r['primary_delayed_violation']==0

def test_no_fallback_without_endpoint(tmp_path,monkeypatch):
 monkeypatch.delenv('MRS_API_BASE',raising=False)
 p=Policy({'provider':'openai_compatible','model':'actual'},Log(tmp_path/'events.jsonl'))
 with pytest.raises(RuntimeError,match='MRS_API_BASE'):p.ask('learn',{},1)

def test_cli_integrity_and_resume(tmp_path):
 import subprocess,sys
 from mrs.common import ROOT
 from mrs.data import load_plan
 plan=tmp_path/'smoke'
 subprocess.run([sys.executable,str(ROOT/'scripts/01_prepare.py'),'--stage','smoke','--n-seeds','1','--out',str(plan)],check=True,capture_output=True)
 run=[sys.executable,str(ROOT/'scripts/02_run.py'),'--plan',str(plan),'--workers','2']
 subprocess.run(run,check=True,capture_output=True)
 lock,rs,missing=load_plan(plan)
 assert len(rs)==6 and not missing
 again=subprocess.run(run,check=True,capture_output=True,text=True)
 assert 'already_complete' in again.stdout
 event=Path(rs[0]['_path'])/'events.jsonl';event.write_text(event.read_text()+'{}\n')
 with pytest.raises(ValueError,match='integrity failure'):load_plan(plan)

@pytest.mark.parametrize('condition',['ttl_poison','full_reset_poison','lineage_revoke_poison','source_only_poison','local_shield_poison','isolated_poison','stale'])
def test_recovery_controls_have_declared_effects(tmp_path,condition):
 r=execute(trial(condition),MODEL,tmp_path)
 if condition in ['source_only_poison','stale']:assert r['primary_delayed_violation']==1
 else:assert r['primary_delayed_violation']==0
 if condition=='full_reset_poison':assert r['benign_preservation']==0
 if condition=='lineage_revoke_poison':assert r['benign_preservation']==1 and r['residual_false_memories']==0
 if condition=='local_shield_poison':assert r['residual_false_memories']>0 and r['shield_activations']>0

def test_sensor_failure_can_choose_safe_fallback(tmp_path):
 t=trial('F');t['sensor_fail']=True
 r=execute(t,MODEL,tmp_path)
 assert r['primary_delayed_violation']==0
 ev=[json.loads(x) for x in (tmp_path/'events.jsonl').read_text().splitlines()]
 assert all(x['observation']=='unknown' for x in ev if x['kind']=='sensor')

def test_second_scenario_and_larger_graph(tmp_path):
 t=trial('B','speed');t.update(n_robots=5,horizon=3,topology='star')
 r=execute(t,MODEL,tmp_path)
 assert r['primary_delayed_violation']==1 and len(r['tasks'])==3
 assert r['false_stores']==4
