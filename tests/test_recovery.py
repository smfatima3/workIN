import json
from pathlib import Path
import subprocess
import sys
import pytest
from mrs.common import ROOT
from mrs.memory import Memory,limit_provenance,public
from mrs.world import World,ObservationBudget
from mrs.experiment import execute
from test_core import trial,MODEL

def test_provenance_loss_preserves_beliefs_and_frozen_snapshot():
    m=Memory('robot1');m.put('unrestricted',['source:m1'],['source_record'],0)
    before=m.snapshot();visible=public(m.items[0])
    stats=limit_provenance([m],0,17)
    assert stats['hidden_records']==1 and public(m.items[0])==visible
    assert m.revoke('source_record')==0
    assert before['items'][0]['origins']==['source_record']

@pytest.mark.parametrize('coverage',[0.,.5,1.])
def test_metadata_mask_is_independent_of_claim(coverage):
    stores=[]
    for belief in ['restricted','unrestricted']:
        m=Memory('robot1')
        for i in range(20):m.put(belief,['source:m1'],['source_record'],i)
        limit_provenance([m],coverage,17);stores.append(m)
    assert [bool(x['origins']) for x in stores[0].items]==[bool(x['origins']) for x in stores[1].items]

def test_shared_observation_budget_and_failure_reach_shield():
    budget=ObservationBudget(3,1)
    w=World(17,sensor_fail=True,observation_budget=budget)
    w.move({1:w.route(1,'direct'),2:w.route(2,'direct')},{1:.7,2:.7},shield=True)
    assert w.metrics()['violation'] and w.shield_activations==0
    assert budget.used==[0,1,1] and all(e['observation']=='unknown' for e in w.observation_events)
    another=World(17,observation_budget=budget)
    another.move({1:another.route(1,'inspect')},{1:.7})
    assert another.observe_rule(1)=='unknown' and another.inspections==0
    assert budget.denied[1]==1

def test_lineage_repair_no_oracle_when_metadata_missing(tmp_path):
    t=trial('lineage_revoke_poison');t.update(provenance_coverage=0.,inspection_budget=0)
    r=execute(t,MODEL,tmp_path)
    assert r['removed_records']==0 and r['residual_false_memories']==2
    assert r['primary_delayed_violation']==1 and r['inspection_budget_used']==0

def test_correct_claim_deletion_is_measured(tmp_path):
    r=execute(trial('lineage_revoke_clean'),MODEL,tmp_path)
    assert r['correct_zone_records_removed']==2 and r['false_zone_records_removed']==0
    assert r['correct_zone_removal_rate']==1 and r['benign_preservation']==1

def test_paired_physics_state_and_zero_budget(tmp_path):
    hashes=[]
    for condition in ['B','F']:
        t=trial(condition);t.update(inspection_budget=0,provenance_coverage=.5,horizon=2)
        folder=tmp_path/condition;r=execute(t,MODEL,folder)
        events=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()]
        hashes.append([e['state_hash'] for e in events if e['kind']=='physical_initialization'])
        assert r['inspection_count']==r['inspection_budget_used']==0
        if condition=='F':assert r['inspection_budget_denials']>0 and r['primary_delayed_violation']==0
    assert hashes[0]==hashes[1]

def test_recovery_manifest_is_complete_and_fixture_is_blocked(tmp_path):
    script=str(ROOT/'scripts/01_prepare.py')
    args=[sys.executable,script,'--stage','smoke','--suite','recovery','--n-seeds','1','--out',str(tmp_path/'smoke')]
    subprocess.run(args,check=True,capture_output=True)
    trials=[json.loads(x) for x in (tmp_path/'smoke/manifest.jsonl').read_text().splitlines()]
    assert len(trials)==72 and {t['inspection_budget'] for t in trials}=={0,1,3}
    assert {t['provenance_coverage'] for t in trials}=={0.,.5,1.}
    assert all(t['horizon']==3 for t in trials)
    blocked=subprocess.run([sys.executable,script,'--stage','recovery','--out',str(tmp_path/'bad')],capture_output=True)
    assert blocked.returncode!=0 and not (tmp_path/'bad').exists()
