from .common import digest
from copy import deepcopy

class Memory:
    def __init__(self,agent): self.agent=agent; self.items=[]; self.counter=0
    def put(self,belief,parents,origin,task,share=True,kind='zone',value=None):
        self.counter+=1
        item=dict(id=f'{self.agent}:m{self.counter}',agent=self.agent,belief=belief,
                  parents=list(parents),origins=sorted(set(origin)),written_task=task,share=share,kind=kind,value=value)
        self.items.append(item); return item
    def retrieve(self,task,ttl=None):
        return [dict(x) for x in self.items if x['kind']=='zone' and (ttl is None or task-x['written_task']<=ttl)]
    def clear(self): self.items=[]
    def revoke(self,origin):
        old=len(self.items); self.items=[x for x in self.items if origin not in x['origins']]; return old-len(self.items)
    def snapshot(self): return {'agent':self.agent,'items':deepcopy(self.items),'hash':digest(self.items)}

def limit_provenance(stores, coverage, seed):
    """Hide whole lineage fields at the recovery boundary, without changing beliefs.

    This models unavailable metadata, not semantic summaries or malicious forgery.
    Selection is deterministic by seed/record ID and independent of truth/condition.
    The earlier immutable event log is evaluator-only, never a repair input.
    """
    if not 0 <= coverage <= 1: raise ValueError('provenance coverage must be in [0,1]')
    total=hidden=0
    for store in stores:
        for record in store.items:
            if record['kind']!='zone': continue
            total+=1
            score=int(digest({'seed':seed,'record_id':record['id'],'mask':'provenance-v1'})[:16],16)/2**64
            if score>=coverage:
                record['parents']=[];record['origins']=[];hidden+=1
    return {'eligible_records':total,'hidden_records':hidden,'coverage_probability':coverage}

def public(item):
    # Evaluator labels never enter policy prompts. Provenance is runtime metadata, not poison labels.
    return {k:item[k] for k in ['id','belief','written_task','kind','value'] if k in item}
