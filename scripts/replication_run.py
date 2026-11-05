import _bootstrap
import argparse,concurrent.futures,itertools,json,traceback
from pathlib import Path
from mrs.common import Log,write_json,read_json,digest,code_hash,file_hash
import mrs.foundation_policy as policy
from mrs.replication_world import WarehouseWorld,warehouse_prompt

MODEL='microsoft/phi-4'
REVISION='2db69c1c3e91a05d2c64a3185acfbaf36f744e25'
CONFIG=dict(thinking=False,temperature=.2,top_p=.95,top_k=20,max_tokens=1024,interface='explicit')


def setup():
    policy.MODEL=MODEL;policy.REVISION=REVISION;policy.CONFIGS['phi']=CONFIG
    original=policy.action_prompt
    policy.action_prompt=lambda *a,**kw:warehouse_prompt(original,*a,**kw)
    import mrs.foundation as f
    f.World=WarehouseWorld;f.action_prompt=policy.action_prompt
    return f


def probes(root,offset=0):
    from foundation_f1 import evaluate,gate
    specs=[dict(configuration='phi',scenario=s,observation=o,wording=w,seed=50000+offset+h*100+i,heldout=bool(h))
        for h in range(2) for i,(s,o,w) in enumerate(itertools.product(['exclusion','speed'],['restricted','unrestricted','unknown'],range(4)))]
    root.mkdir(parents=True)
    write_json(root/'manifest.json',specs)
    write_json(root/'protocol.lock.json',dict(model=MODEL,revision=REVISION,config=CONFIG,code_hash=code_hash(),manifest_hash=digest(specs),
        purpose='fixed clean configuration; 24 screening and 24 fresh paraphrases; no attack selection'))
    def one(spec):
        p=root/str(spec['seed']);p.mkdir();log=Log(p/'events.jsonl');pcy=policy.FoundationPolicy('phi',log)
        row=dict(spec)
        try:
            response=pcy.ask('act',policy.action_prompt(spec['scenario'],spec['observation'],[],wording=spec['wording'],heldout=spec['heldout']),spec['seed'])
            row.update(response=response,metrics=evaluate(response,spec['scenario'],spec['observation']))
        except Exception as e:row['error']=str(e)
        row.update(calls=pcy.calls,tokens_in=pcy.tokens_in,tokens_out=pcy.tokens_out)
        log.finalize();write_json(p/'result.json',row);return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:rows=list(pool.map(one,specs))
    result={'screen_gate':gate(rows[:24]),'heldout_gate':gate(rows[24:]),'rows':rows,'model':MODEL,'revision':REVISION}
    write_json(root/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
    return result['screen_gate'] and result['heldout_gate']


def cohort(root,stage,f,offset=0):
    from foundation_run import specifications,branches
    from foundation_analyze import analyze
    from mrs.foundation_hooks import ACTIVE_GUARD
    from mrs.maple_adapter import MapleGuard,UPSTREAM,EMBED_MODEL,EMBED_REVISION
    root.mkdir(parents=True,exist_ok=False)
    specs=specifications('f23',development_offset=40000+offset) if stage=='f23' else [s for s in specifications('f456') if s['variant']<5]
    if stage!='f23':
        for s in specs:s['seed']+=40000
        extra=[]
        for s in specs:
            if s['stage']=='F4' and s['condition'] in 'AB':
                extra.append(dict(s,stage='MAPLE',parent_id=s['parent_id']+'_MAPLE',published_guard=True))
        specs+=extra
    def branch(s):return [('MAPLE','unchanged','free',False,0)] if s.get('published_guard') else branches(s)
    intended=[dict(parent_id=s['parent_id'],stage=st,branch=b,cost=c,notice=n,replicate=r) for s in specs for st,b,c,n,r in branch(s)]
    manifest=dict(parents=specs,continuations=intended)
    write_json(root/'manifest.json',manifest)
    write_json(root/'protocol.lock.json',dict(stage=stage,configuration='phi',config=CONFIG,model=MODEL,revision=REVISION,
        code_hash=code_hash(),manifest_hash=digest(manifest),workers=16,primary_family_size=12,
        upstream_MAPLE=UPSTREAM,embedding_model=EMBED_MODEL,embedding_revision=EMBED_REVISION,
        scope='cross-model/cross-task exploratory replication; joint change cannot isolate model versus scene',
        feedback='MAPLE outcome update sees service arrival only, never privileged safety truth',
        baseline_contrast='lifecycle MAPLE clean/false versus matched F4 A/B; not a post-incident F6 repair',
        replay_selection='F4_exclusion_1_0_B regardless of outcome; first task; F5 unchanged/correct r0 and F6 verify physical'))
    def job(s):
        token=ACTIVE_GUARD.set(MapleGuard() if s.get('published_guard') else None)
        parent=root/'parents'/s['parent_id']
        try:
            cp=f.acquire(s,'phi',parent)
            for st,b,c,n,r in branch(s):
                dest=root/'continuations'/s['parent_id']/f'{st}_{b}_{c}_r{r}'
                try:
                    f.continue_parent(cp,b,'phi',dest,c,n,r)
                    print(json.dumps({'parent':s['parent_id'],'stage':st,'branch':b,'status':'completed'}),flush=True)
                except Exception as e:
                    dest.mkdir(exist_ok=True,parents=True);write_json(dest/'FAILED.json',{'error':str(e),'traceback':traceback.format_exc()})
                    print(json.dumps({'parent':s['parent_id'],'stage':st,'branch':b,'status':'failed'}),flush=True)
        except Exception as e:
            parent.mkdir(exist_ok=True,parents=True);write_json(parent/'FAILED.json',{'error':str(e),'traceback':traceback.format_exc()})
            print(json.dumps({'parent':s['parent_id'],'status':'failed_acquisition'}),flush=True)
        finally:ACTIVE_GUARD.reset(token)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:list(pool.map(job,specs))
    result=analyze(root)
    print(json.dumps({'completion':result['completion'],'gates':result['gates'],'validation':result['validation']}),flush=True)
    return result


def main(stage,out,gate_path,offset=0):
    root=Path(out);root.mkdir(parents=True,exist_ok=False);f=setup()
    if stage=='gate':
        if not probes(root/'f1',offset):raise RuntimeError('Independent model F1 gate failed; no attack run')
        cohort(root/'data','f23',f,offset)
    else:
        gate=read_json(Path(gate_path)/'data/analysis/summary.json')
        if not gate['gates']['F2']['passed'] or not gate['gates']['F3_clean']['passed']:raise RuntimeError('Independent model clean memory gate failed')
        write_json(root/'gate_evidence.json',{'path':gate_path,'sha256':file_hash(Path(gate_path)/'data/analysis/summary.json')})
        cohort(root/'data','f456',f)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['gate','main'],required=True);p.add_argument('--out',required=True)
    p.add_argument('--gate-path',default='/evidence/replication_phi4_gate_v2/run');p.add_argument('--offset',type=int,default=0)
    a=p.parse_args();main(a.stage,a.out,a.gate_path,a.offset)
