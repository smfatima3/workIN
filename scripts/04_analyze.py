import _bootstrap
import argparse,csv,json
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mrs.data import load_plan
from mrs.common import write_json
from mrs.statistics import wilson,bootstrap_mean,paired_binary,signflip_p,holm,bounded_mean_ci
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--allow-partial',action='store_true');a=p.parse_args()
lock,results,missing=load_plan(a.plan,a.allow_partial);out=Path(a.plan)/'analysis';out.mkdir(exist_ok=True)
if not results:raise SystemExit('No completed trials')
scalar=['primary_delayed_violation','safe_task_completion','task_completion','contact_any','max_contact_force_N','normal_contact_impulse_Ns',
 'min_zone_clearance_m','min_robot_gap_m','mean_mission_time_s','mean_path_length_m','unsafe_request_rate','refusal_rate','inspection_count',
 'shield_activations','false_stores','learn_events','retrieved_items','false_retrievals','residual_false_memories','benign_preservation','removed_records',
 'model_calls','prompt_tokens','completion_tokens','model_latency_s','write_inspection_time_s','total_sim_time_s','wall_time_s',
 'provenance_eligible_records','provenance_hidden_records','correct_zone_records_removed','false_zone_records_removed',
 'correct_zone_removal_rate','inspection_budget_denials','inspection_budget_used']
defaults={'provenance_coverage':1.,'inspection_budget':None,'dock_lookup_delay_s':4.}
strata=['scenario','restricted','n_robots','topology','delay_tasks','sensor_fail','provenance_coverage','inspection_budget','dock_lookup_delay_s']
rows=[{**{k:r['trial'][k] for k in ['trial_id','block_id','condition','scenario','restricted','seed','n_robots','topology','delay_tasks','sensor_fail']},
       **{k:r['trial'].get(k,v) for k,v in defaults.items()},**{k:r.get(k) for k in scalar},'fixture':r['fixture']} for r in results]
with (out/'run_metrics.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups=defaultdict(list)
for r in results:
 t=r['trial'];key=tuple(t.get(x,defaults.get(x)) for x in strata);groups[key].append(r)
summary=[];contrasts=[]
for key,rr in groups.items():
 by=defaultdict(list)
 for r in rr:by[r['trial']['condition']].append(r)
 for c,rs in by.items():
  entry={'stratum':list(key),'condition':c,'n_rollouts':len(rs)}
  for m in scalar:
   vals=[r[m] for r in rs if r.get(m) is not None]
   entry[m]={'n':len(vals),'mean':float(np.mean(vals)) if vals else None,
             'ci95':wilson(sum(vals),len(vals)) if m in ['primary_delayed_violation','contact_any'] else bootstrap_mean(vals)}
  for m in ['safe_task_completion','task_completion','unsafe_request_rate','refusal_rate','benign_preservation']:
   vals=[r[m] for r in rs if r[m] is not None];entry[m]['conservative_bounded_ci95']=bounded_mean_ci(vals)
  summary.append(entry)
 pairmap=defaultdict(dict)
 for r in rr:pairmap[r['trial']['block_id']][r['trial']['condition']]=r
 comparisons=[('poison_effect','B','A'),('defense_effect','F','B')]
 comparisons += [(c+'_vs_B',c,'B') for c in sorted(by) if c.endswith('_poison') and not c.startswith('isolated')]
 for label,ca,cb in comparisons:
  pairs=[d for d in pairmap.values() if ca in d and cb in d]
  if pairs:
   res=paired_binary([d[ca]['primary_delayed_violation'] for d in pairs],[d[cb]['primary_delayed_violation'] for d in pairs])
   contrasts.append({'stratum':list(key),'contrast':label,**res,'primary_family':bool(key[1]) and label in ['poison_effect','defense_effect'],'secondary_family':label not in ['poison_effect','defense_effect'],'estimand':ca+' minus '+cb})
 pairs=[d for d in pairmap.values() if all(c in d for c in 'ABCD')]
 if pairs:
  diff=[d['B']['primary_delayed_violation']-d['A']['primary_delayed_violation']-d['D']['primary_delayed_violation']+d['C']['primary_delayed_violation'] for d in pairs]
  contrasts.append({'stratum':list(key),'contrast':'memory_interaction','n':len(pairs),'difference':float(np.mean(diff)),
                    'paired_bootstrap_ci95':bootstrap_mean(diff),'p':signflip_p(diff),'primary_family':False,
                    'estimand':'(B-A)-(D-C)','test_note':'sign symmetry permutation diagnostic; not exact factorial randomization inference'})
 # Every recovery gets paired clean AND poisoned utility/cost, not just E versus A.
 utility_pairs=[('E','A'),('F','B')]+[(c,'A' if c.endswith('_clean') else 'B') for c in sorted(by)
               if c.endswith(('_clean','_poison')) and not c.startswith('isolated')]
 for ca,cb in utility_pairs:
  pairs=[d for d in pairmap.values() if ca in d and cb in d]
  if not pairs:continue
  for metric in ['task_completion','safe_task_completion','benign_preservation','mean_mission_time_s','inspection_count','model_calls']:
   diff=[d[ca][metric]-d[cb][metric] for d in pairs]
   entry={'stratum':list(key),'contrast':f'{ca}_vs_{cb}_{metric}','metric':metric,'n':len(pairs),
          'difference':float(np.mean(diff)),'paired_bootstrap_ci95':bootstrap_mean(diff),
          'primary_family':False,'estimand':ca+' minus '+cb,'noninferiority_status':'not_established_requires_precision_review'}
   if metric in ['task_completion','safe_task_completion','benign_preservation']:
    entry['conservative_ci95']=bounded_mean_ci(diff,lower=-1,upper=1)
    entry['noninferiority_margin']=lock['utility_margin_absolute']
   contrasts.append(entry)
 for ca,cb in [('lineage_revoke_poison','full_reset_poison'),('lineage_revoke_poison','F'),('F','full_reset_poison')]:
  pairs=[d for d in pairmap.values() if ca in d and cb in d]
  if pairs:
   res=paired_binary([d[ca]['primary_delayed_violation'] for d in pairs],[d[cb]['primary_delayed_violation'] for d in pairs])
   contrasts.append({'stratum':list(key),'contrast':ca+'_vs_'+cb,**res,'primary_family':False,'secondary_family':True,'estimand':ca+' minus '+cb})
primary=[c for c in contrasts if c['primary_family'] and 'p' in c]
for c,adj in zip(primary,holm([c['p'] for c in primary])):c['holm_p']=adj
secondary=[c for c in contrasts if c.get('secondary_family') and 'p' in c]
for c,adj in zip(secondary,holm([c['p'] for c in secondary])):c['secondary_holm_p']=adj
write_json(out/'summary.json',{'purpose':lock['purpose'],'fixture':any(r['fixture'] for r in results),'missing_trials':missing,'stratum_fields':strata,'summary':summary,'contrasts':contrasts})
# One figure per stratum; all outcomes and all conditions remain available in CSV/JSON.
for idx,(key,rr) in enumerate(sorted(groups.items(),key=lambda kv:repr(kv[0]))):
 cs=sorted(set(r['trial']['condition'] for r in rr));fig,axs=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
 for ax,metric,title in zip(axs,['primary_delayed_violation','safe_task_completion'],['Delayed rule violation','Safe task completion']):
  for j,c in enumerate(cs):
   vals=[r[metric] for r in rr if r['trial']['condition']==c];mean=np.mean(vals)
   ci=wilson(sum(vals),len(vals)) if metric=='primary_delayed_violation' else bounded_mean_ci(vals)
   ax.bar(j,mean,color='#276b86' if metric=='safe_task_completion' else '#bf5c45')
   if ci[0] is not None:ax.errorbar(j,mean,yerr=[[max(0,mean-ci[0])],[max(0,ci[1]-mean)]],color='black',capsize=3)
   ax.text(j,min(1.08,mean+.07),f'n={len(vals)}',ha='center',fontsize=8)
  ax.set(xticks=range(len(cs)),xticklabels=cs,ylim=(0,1.16),title=title,ylabel='Rollout-level proportion / mean')
  ax.tick_params(axis='x',rotation=55)
 label='SOFTWARE TEST — SCRIPTED POLICY' if lock['purpose']=='software_validation_only' else lock['stage'].upper()
 stratum_label=f'{key[0].title()} | '+('restricted' if key[1] else 'unrestricted')+f' | {key[2]} robots | {key[3]} | provenance {key[6]} | sensing budget {key[7]} | sensor failed {key[5]} | dock cost {key[8]}s'
 fig.suptitle(f'{label}\n{stratum_label}');fig.savefig(out/f'outcomes_{idx}.png',dpi=160);fig.savefig(out/f'outcomes_{idx}.pdf');plt.close(fig)
lines=['# Analysis report',f"Purpose: {lock['purpose']}. Completed {len(results)}/{lock['trials']}.",
'Each independent unit is a complete rollout. Repeated tasks and robot messages are not independent samples.',
'Rule violations and contact proxies are not injury estimates. Bootstrap intervals may be degenerate at small n; primary binary differences also include conservative intervals.',
'No scientific conclusion is licensed by scripted-policy results.' if lock['purpose']=='software_validation_only' else 'Inspect uncertainty, clean task cost, missingness, and prior-work controls before making a claim.',
'','## Contrasts']
for c in contrasts:lines.append(f"- {c['stratum']} {c['contrast']}: n={c['n']}, difference={c['difference']:.3f}, interval={c.get('conservative_ci95',c['paired_bootstrap_ci95'])}")
(out/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'output':str(out.resolve()),'complete':not missing,'rollouts':len(results)},indent=2))
