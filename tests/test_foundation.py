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
