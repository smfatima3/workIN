import _bootstrap
import argparse,json
import numpy as np
from mrs.common import read_json,write_json
p=argparse.ArgumentParser(description='Finite-horizon algebraic diagnostic, not a fitted safety guarantee.')
p.add_argument('--input',required=True);p.add_argument('--out',required=True);a=p.parse_args();d=read_json(a.input)
K=np.array(d['K'],float);z=np.array(d['z0'],float);q=np.array(d['q'],float);H=int(d['horizon'])
if K.shape!=(len(z),len(z)) or q.shape!=z.shape or np.any(K<0) or np.any(z<0) or np.any(q<0) or np.any(q>1) or H<0:raise SystemExit('Invalid nonnegative operator, population, hazard bounds, or horizon')
terms=[]
for g in range(H+1):terms.append(float(q@z));z=K@z
r={'spectral_radius':float(max(abs(np.linalg.eigvals(K)))),'horizon':H,'generation_hazard_weights':terms,
   'finite_horizon_union_bound':min(1.,sum(terms)), 'status':d.get('status','unverified_inputs'),
   'assumptions':'Each generation expected count bounded by K times previous counts; q bounds conditional per-item hazard probability. No independence needed for union bound; fitted point estimates alone do not satisfy these bounds.',
   'interpretation':'rho(K)<1 does not imply zero finite-horizon physical risk. A nilpotent finite relay can transmit a harmful claim with rho(K)=0.'}
write_json(a.out,r);print(json.dumps(r,indent=2))
