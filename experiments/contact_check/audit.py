"""Audit the rerun against the immutable supplied package and original Qwen rows."""
import argparse
import csv
import hashlib
import io
import json
import platform
import zipfile
from pathlib import Path
import importlib.metadata
import imageio.v2 as imageio


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def audit(root, supplied, qwen):
    root, supplied, qwen = map(Path, (root, supplied, qwen))
    rows = list(csv.DictReader((root/'calibration.csv').open()))
    source = list(csv.DictReader(qwen.open()))
    with zipfile.ZipFile(supplied) as z:
        expected = list(csv.DictReader(io.StringIO(z.read('contact_check/calibration.csv').decode())))
        assert rows == expected
        assert (root/'placement_trace.json').read_bytes() == z.read('contact_check/placement_trace.json')
        originals = z.read('contact_check/original_qwen_event_rows.csv')
        assert (root/'original_qwen_event_rows.csv').read_bytes() == originals
        assert all(r in source for r in csv.DictReader(io.StringIO(originals.decode())))
    metrics = []
    summaries = []
    for case in ('A_standard','B_standard','C_standard','C_paused'):
        for offset in (-.02, 0., .02):
            pair = [root/'trials'/f'{case}_{arm}_{offset:+.2f}' for arm in ('reference','challenge')]
            ds = [json.loads((p/'evidence.json').read_text()) for p in pair]
            assert ds[0]['initial_state_hash'] == ds[1]['initial_state_hash']
            assert (pair[0]/'scene.xml').read_bytes() == (pair[1]/'scene.xml').read_bytes()
            for arm, d in zip(('reference','challenge'),ds):
                contacts=d['contact_steps']
                assert len(d['frames'])==95 and d['steps']==950 and d['dt_s']==.002
                assert all({e['geom1'],e['geom2']}=={'moving','person'} and e['normal_force_n']>0 for e in contacts)
                row=next(r for r in rows if (r['scenario']+'_'+r['motion'],r['action'],float(r['person_x_offset_m']))==(case,arm,offset))
                assert int(row['contact'])==bool(contacts)
                metrics.append(dict(trial_id=f'{case}_{arm}_{offset:+.2f}',scenario=case,action=arm,offset_m=offset,
                    contact=int(bool(contacts)),first_contact_physics_time_s=contacts[0]['time_s'] if contacts else None,
                    max_normal_force_n=d['max_normal_force_n'],normal_impulse_ns=d['normal_impulse_ns'],
                    contact_steps=len(contacts),initial_state_hash=d['initial_state_hash']))
        arms={arm:[r for r in rows if r['scenario']+'_'+r['motion']==case and r['action']==arm] for arm in ('reference','challenge')}
        summaries.append({'scenario':case,**{a:{'contacts':sum(int(r['contact']) for r in rs),'trials':len(rs)} for a,rs in arms.items()}})
        reader=imageio.get_reader(root/'videos'/(case+'.mp4'))
        assert reader.count_frames()==96 and reader.get_meta_data()['fps']==12
        assert reader.get_data(95).shape==(960,1280,3)
        reader.close()
    with (root/'contact_metrics.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=metrics[0]);writer.writeheader();writer.writerows(metrics)
    results=dict(validation='PASS',trial_count=24,matched_initial_pairs=12,model_calls=0,
        original_rows_verified=2,supplied_archive_sha256=sha(supplied),source_qwen_csv_sha256=sha(qwen),
        summary=summaries,environment={'python':platform.python_version(),**{n:importlib.metadata.version(n) for n in ('mujoco','numpy','Pillow','imageio','imageio-ffmpeg')}})
    (root/'audit.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--supplied',required=True);p.add_argument('--qwen-csv',required=True)
    a=p.parse_args();audit(a.root,a.supplied,a.qwen_csv)
