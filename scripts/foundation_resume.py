"""Resume an immutable scientific cohort; preserve every interrupted attempt."""
import argparse, concurrent.futures, json, shutil, sys, traceback
from pathlib import Path


def main(source, root):
    source, root = Path(source), Path(root)
    sys.path[:0] = [str(source/'scripts'), str(source/'src')]
    from mrs.common import read_json, write_json, code_hash, digest, file_hash
    from mrs.foundation import acquire, continue_parent
    from foundation_analyze import analyze
    lock = read_json(root/'protocol.lock.json')
    manifest = read_json(root/'manifest.json')
    assert code_hash() == lock['code_hash'], 'Scientific source differs from frozen cohort'
    assert digest(manifest) == lock['manifest_hash']
    configuration = lock['configuration']
    attempts = root/'interrupted_attempts'
    reused = []
    # Validate all completed files before any new model calls.
    for p in root.glob('continuations/*/*/DONE.json'):
        for name, expected in read_json(p)['hashes'].items():
            assert file_hash(p.parent/name) == expected, str(p.parent/name)
        reused.append(str(p.parent.relative_to(root)))
    write_json(root/'RESUME.json', {'reused_completed':sorted(reused),
        'scientific_code_hash':code_hash(), 'sampling_and_manifest':'unchanged',
        'interrupted_calls':'retained; incomplete acquisition/branch restarted with original seeds',
        'numerical_limit':'new server/batch scheduling may affect floating-point sampled outputs'})

    def preserve(path):
        if path.exists():
            target=attempts/path.relative_to(root)
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():raise RuntimeError('Refusing to overwrite interrupted evidence')
            shutil.move(str(path),str(target))

    def job(spec):
        parent=root/'parents'/spec['parent_id']
        try:
            if (parent/'checkpoint.json').exists() and (parent/'events.jsonl').exists():
                cp=read_json(parent/'checkpoint.json')
                assert cp['spec']==spec
                assert digest({k:v for k,v in cp.items() if k!='checkpoint_hash'})==cp['checkpoint_hash']
            else:
                preserve(parent)
                cp=acquire(spec,configuration,parent)
        except Exception as e:
            parent.mkdir(parents=True,exist_ok=True)
            write_json(parent/'RESUME_FAILED.json',{'error':str(e),'traceback':traceback.format_exc()})
            print(json.dumps({'parent':spec['parent_id'],'status':'failed_acquisition'}),flush=True)
            return
        for entry in manifest['continuations']:
            if entry['parent_id']!=spec['parent_id']:continue
            dest=root/'continuations'/spec['parent_id']/f"{entry['stage']}_{entry['branch']}_{entry['cost']}_r{entry['replicate']}"
            if (dest/'DONE.json').exists():continue
            preserve(dest)
            try:
                continue_parent(cp,entry['branch'],configuration,dest,entry['cost'],entry['notice'],entry['replicate'])
                print(json.dumps({**entry,'status':'completed'}),flush=True)
            except Exception as e:
                dest.mkdir(parents=True,exist_ok=True)
                write_json(dest/'FAILED.json',{'error':str(e),'traceback':traceback.format_exc()})
                print(json.dumps({**entry,'status':'failed'}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=lock['workers']) as pool:
        list(pool.map(job,manifest['parents']))
    result=analyze(root)
    print(json.dumps({'completion':result['completion'],'gates':result['gates'],'validation':result['validation']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--root',required=True)
    a=p.parse_args();main(a.source,a.root)
