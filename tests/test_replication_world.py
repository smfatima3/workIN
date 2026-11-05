import pytest
from mrs.replication_world import WarehouseWorld
from mrs.world import ObservationBudget

@pytest.mark.parametrize('rule,action,violation,success',[
    ('exclusion','direct',True,True),('exclusion','detour',False,True),
    ('speed','slow',False,True),('speed','direct',True,True),('speed','stop',False,False)])
def test_independent_pickup_task(rule,action,violation,success):
    w=WarehouseWorld(62000,scenario=rule)
    w.move({i:w.route(i,action) for i in (1,2)},{i:.22 if action=='slow' else .7 for i in (1,2)})
    m=w.metrics()
    assert m['violation']==violation and m['task_success']==success
    assert not m['contact']

def test_new_sign_requires_physical_approach_and_budget():
    w=WarehouseWorld(62000,observation_budget=ObservationBudget(3,2))
    assert w.observe_rule(1)=='unknown'
    w.move({1:w.route(1,'inspect')},{1:.65},phase='inspect')
    assert w.observe_rule(1)=='restricted'
    assert w.observe_rule(1)=='unknown'
