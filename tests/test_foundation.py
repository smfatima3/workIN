from copy import deepcopy
import numpy as np
from mrs.world import World,ObservationBudget
from mrs.foundation import freeze_world,restore_world,state_vector,fresh_stores,intervene
from mrs.common import digest

def checkpoint():
    stores=fresh_stores(12)
    for s in stores[1:]:s.put('unrestricted',[],['robot0:m3'],0,value='delivery_zone')
    return dict(stores=[s.snapshot() for s in stores],source_record_id='robot0:m3',
                spec={'restricted':True},worlds=[freeze_world(World(12),12)])

def test_checkpoint_restores_full_physics_and_identical_continuation():
    a=World(12);snap=freeze_world(a,12);b=restore_world(snap,ObservationBudget(3,3))
    for w in (a,b):w.move({1:w.route(1,'detour'),2:w.route(2,'detour')},{1:.7,2:.7})
    assert np.allclose(state_vector(a),state_vector(b),rtol=0,atol=1e-12)
    assert a.metrics()==b.metrics()

def test_memory_forks_leave_parent_physics_and_nontarget_fields_unchanged():
    cp=checkpoint();before=deepcopy(cp)
    stores,edit=intervene(cp,'correct')
    assert cp==before and edit['oracle_correction']
    for old,s in zip(cp['stores'],stores):
        for a,b in zip(old['items'],s.items):
            assert {k:v for k,v in a.items() if k!='belief'}=={k:v for k,v in b.items() if k!='belief'}
    assert edit['physical_checkpoint_hash']==digest(cp['worlds'])
    sham,_=intervene(cp,'sham')
    assert all(r['belief']=='unrestricted' for s in sham for r in s.items if r['kind']=='zone')

def test_lineage_repair_and_noop_do_not_consult_truth():
    cp=checkpoint();a,_=intervene(cp,'lineage');cp['spec']['restricted']=False;b,_=intervene(cp,'lineage')
    assert [s.items for s in a]==[s.items for s in b]
    assert all(r['kind']!='zone' for s in a for r in s.items)
    cp['stores']=[s.snapshot() for s in a]
    _,edit=intervene(cp,'correct');assert not edit['changed']

def test_real_dock_reacquisition_and_authorization_gate(tmp_path,monkeypatch):
    import mrs.foundation as f
    class Fixture:
        config={'interface':'explicit'}
        def __init__(self,*a):self.calls=0;self.tokens_in=0;self.tokens_out=0;self.latency=0.
        def ask(self,*a):
            self.calls+=1
            return dict(action='detour',belief='unknown',reason='UNIT TEST ONLY')
    monkeypatch.setattr(f,'FoundationPolicy',Fixture)
    spec=dict(parent_id='fixture',stage='TEST',seed=12,scenario='exclusion',restricted=True,horizon=1,acquisition='controlled')
    cp=f.acquire(spec,'explicit',tmp_path/'parent')
    real=f.continue_parent(cp,'full_reset','explicit',tmp_path/'real',cost='physical',notice=True)
    free=f.continue_parent(cp,'full_reset','explicit',tmp_path/'free',cost='free',notice=True)
    assert real['dock_reads']==free['dock_reads']==2
    assert real['dock_motion_s']>0 and free['dock_motion_s']==0
    assert real['task_completion']==free['task_completion']==1
    assert real['benign_retention']==free['benign_retention']==0
    assert real['physical_checkpoint_hash']==free['physical_checkpoint_hash']
    bad=deepcopy(cp)
    for s in bad['stores'][1:]:
        for r in s['items']:
            if r['kind']=='dock_code':r['value']='incorrect'
    bad['checkpoint_hash']=digest({k:v for k,v in bad.items() if k!='checkpoint_hash'})
    denied=f.continue_parent(bad,'unchanged','explicit',tmp_path/'denied')
    assert denied['task_completion']==0 and denied['tasks'][0]['physical_arrival']
