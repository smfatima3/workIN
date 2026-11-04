import _bootstrap
import argparse,json,math
import numpy as np
from scipy.stats import norm
p=argparse.ArgumentParser(description='Design sensitivity for paired binary differences; assumptions, not observed results.')
p.add_argument('--p10',type=float,default=.20,help='P(poison violation, clean no violation)')
p.add_argument('--p01',type=float,default=.05,help='P(clean violation, poison no violation)')
p.add_argument('--alpha',type=float,default=.05);p.add_argument('--comparisons',type=int,default=6);p.add_argument('--power',type=float,default=.8)
p.add_argument('--half-width',type=float,default=.10);a=p.parse_args()
if min(a.p10,a.p01)<0 or a.p10+a.p01>1 or a.p10==a.p01:raise SystemExit('Need valid non-equal discordance probabilities')
d=a.p10-a.p01;s=a.p10+a.p01;alpha=a.alpha/a.comparisons
n=math.ceil(((norm.ppf(1-alpha/2)*math.sqrt(s)+norm.ppf(a.power)*math.sqrt(s-d*d))/abs(d))**2)
precision=math.ceil(norm.ppf(.975)**2*(s-d*d)/a.half_width**2)
print(json.dumps({'assumptions':vars(a),'normal_approx_n_pairs_per_stratum':n,'approx_precision_n_pairs':precision,
 'recommendation_n':max(n,precision),'caution':'Design approximation, not a guarantee. Rare events and noninferiority need dedicated precision review. Sample sizes refer to independent paired rollouts, not messages or task repetitions.'},indent=2))
