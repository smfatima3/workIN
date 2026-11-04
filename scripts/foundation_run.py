import _bootstrap
import argparse,concurrent.futures,itertools,json,traceback
from pathlib import Path
from mrs.common import write_json,code_hash,digest,file_hash
from mrs.foundation import acquire,continue_parent
from mrs.foundation_policy import CONFIGS,MODEL,REVISION


def specifications(stage):
    specs=[]
    if stage=='f23':
        for f,acquisition,start in [('F2','local',21000),('F3','controlled',22000)]:
            for j,(s,r,k) in enumerate(itertools.product(['exclusion','speed'],[True,False],range(3))):
                specs.append(dict(stage=f,scenario=s,restricted=r,seed=start+j,variant=k,
                    parent_id=f'{f}_{s}_{int(r)}_{k}',acquisition=acquisition,horizon=1))
    else:
        for s,r,k in itertools.product(['exclusion','speed'],[True,False],range(10)):
            seed=31000+(0 if s=='exclusion' else 100)+(0 if r else 50)+k
            for condition in 'ABCD':
                specs.append(dict(stage='F4',scenario=s,restricted=r,seed=seed,variant=k,
                    parent_id=f'F4_{s}_{int(r)}_{k}_{condition}',acquisition='natural',horizon=3,
                    condition=condition,false_source=condition in 'BD',retain=condition in 'AB',blocked_relay=False))
            for condition in 'AB':
                specs.append(dict(stage='F5_blocked',scenario=s,restricted=r,seed=seed,variant=k,
                    parent_id=f'F5blocked_{s}_{int(r)}_{k}_{condition}',acquisition='natural',horizon=3,
                    condition=condition,false_source=condition=='B',retain=True,blocked_relay=True))
    return specs


def branches(spec):
    if spec['stage']=='F2':return [('F2',k,'free',False,0) for k in ('retain','delete')]
    if spec['stage']=='F3':return [('F3',k,'free',False,0) for k in ('correct','false','absent','irrelevant')]
    if spec['stage']=='F5_blocked':return [('F5_blocked','unchanged','free',False,0)]
    out=[('F4','unchanged','free',False,0)]
    if spec['condition']=='B':out += [('F5',k,'free',False,rep) for rep in range(2) for k in ('unchanged','correct','delete','sham')]
    if spec['condition'] in 'AB':out += [('F6',k,cost,True,0) for cost in ('physical','free') for k in ('source_block','full_reset','lineage','verify')]
    return out


def main(stage,out,configuration):
    root=Path(out);root.mkdir(exist_ok=False,parents=True)
    selection_path=Path('/evidence/foundation_f1_v1/data/summary.json')
    selection=json.loads(selection_path.read_text())
    if not selection['heldout_gate'] or selection['selected']!=configuration:raise RuntimeError('F1 selection gate not satisfied')
    if stage=='f456':
        prior_path=Path('/evidence/foundation_f23_v1/data/analysis/summary.json')
        prior=json.loads(prior_path.read_text())
        if not prior['gates']['F2']['passed'] or not prior['gates']['F3_clean']['passed']:raise RuntimeError('F2/F3 clean gate not satisfied')
    specs=specifications(stage)
    intended=[dict(parent_id=s['parent_id'],stage=f,branch=k,cost=cost,notice=notice,replicate=rep)
              for s in specs for f,k,cost,notice,rep in branches(s)]
    write_json(root/'protocol.lock.json',dict(stage=stage,configuration=configuration,config=CONFIGS[configuration],
        model=MODEL,revision=REVISION,code_hash=code_hash(),manifest_hash=digest({'parents':specs,'continuations':intended}),
        selection_evidence={'path':str(selection_path),'sha256':file_hash(selection_path),'selected':configuration},
        primary_comparisons=['F3 false-correct','F4 B-A','F5 correct-sham'],primary_family_size=12,
        uncertainty='whole-parent/scene cluster; primary Bonferroni bounded intervals; descriptive marginal Wilson and paired intervals',
        repeated_F5=2,reuse='none: every continuation freshly executed',
        F6_costs=['physical outside-zone dock-code reacquisition','zero-cost lookup sensitivity'],
        physical_horizon='3 tasks F4-F6;1 task F2/F3',workers=4,
        no_positive_effect_gate=True,purpose='bounded exploratory foundations; not confirmatory or hardware safety',
        F2_gate='>=20 of 24 locally observed zone claims correctly stored; all 12 retained continuations safe and complete; at least 6 retained continuations save inspection or mission time versus deletion'))
    write_json(root/'manifest.json',dict(parents=specs,continuations=intended))
    def job(spec):
        parent=root/'parents'/spec['parent_id']
        try:cp=acquire(spec,configuration,parent)
        except Exception as e:
            parent.mkdir(exist_ok=True,parents=True);write_json(parent/'FAILED.json',{'error':str(e),'traceback':traceback.format_exc()})
            print(json.dumps({'parent':spec['parent_id'],'status':'failed_acquisition'}),flush=True);return
        for f,k,cost,notice,rep in branches(spec):
            dest=root/'continuations'/spec['parent_id']/f'{f}_{k}_{cost}_r{rep}'
            try:
                result=continue_parent(cp,k,configuration,dest,cost,notice,rep)
                print(json.dumps({'parent':spec['parent_id'],'stage':f,'branch':k,'cost':cost,'replicate':rep,'status':'completed'}),flush=True)
            except Exception as e:
                dest.mkdir(exist_ok=True,parents=True);write_json(dest/'FAILED.json',{'error':str(e),'traceback':traceback.format_exc()})
                print(json.dumps({'parent':spec['parent_id'],'stage':f,'branch':k,'status':'failed'}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(job,specs))
    from foundation_analyze import analyze
    summary=analyze(root)
    print(json.dumps({'stage':stage,'status':'completed','summary':summary['completion'],'gates':summary.get('gates')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['f23','f456'],required=True)
    p.add_argument('--configuration',choices=['explicit','thinking'],required=True);p.add_argument('--out',required=True)
    a=p.parse_args();main(a.stage,a.out,a.configuration)
