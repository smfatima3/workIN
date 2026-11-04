import numpy as np
from scipy.stats import binomtest

def wilson(k,n,z=1.95996398454):
 if n==0:return [None,None]
 p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return [float(max(0,center-half)),float(min(1,center+half))]

def bootstrap_mean(x,seed=4201,reps=5000):
 x=np.asarray(x,float)
 if len(x)<2:return [None,None]
 rng=np.random.default_rng(seed);means=np.mean(x[rng.integers(0,len(x),(reps,len(x)))],axis=1)
 return np.quantile(means,[.025,.975]).tolist()

def signflip_p(x,seed=331,reps=10000):
 x=np.asarray(x,float);n=len(x)
 if n==0:return None
 observed=abs(float(x.mean()));rng=np.random.default_rng(seed)
 if n<=16:
  signs=2*((np.arange(2**n)[:,None]>>np.arange(n))&1)-1
  return float(np.mean(np.abs(np.mean(signs*x,axis=1))>=observed-1e-12))
 null=np.mean(rng.choice([-1,1],(reps,n))*x,axis=1)
 return float((1+np.sum(abs(null)>=observed-1e-12))/(reps+1))

def paired_binary(a,b):
 a=np.asarray(a,int);b=np.asarray(b,int);d=a-b
 n10=int(np.sum((a==1)&(b==0)));n01=int(np.sum((a==0)&(b==1)))
 p=1. if n10+n01==0 else float(binomtest(n10,n10+n01,.5).pvalue)
 # Conservative paired risk-difference interval by Bonferroni Wilson bounds
 # on the two discordant multinomial cells; avoids a zero-width all-zero CI.
 lo10,hi10=wilson(n10,len(a),2.2414027276);lo01,hi01=wilson(n01,len(a),2.2414027276)
 return {'n':len(a),'difference':float(d.mean()),'paired_bootstrap_ci95':bootstrap_mean(d),
         'conservative_ci95':[max(-1.,lo10-hi01),min(1.,hi10-lo01)],'n10':n10,'n01':n01,'p':p}

def holm(pvalues):
 order=np.argsort(pvalues);out=np.zeros(len(order));last=0.
 for i,k in enumerate(order):last=max(last,min(1.,(len(order)-i)*pvalues[k]));out[k]=last
 return out.tolist()


def bounded_mean_ci(x,lower=0.,upper=1.,alpha=.05):
 x=np.asarray(x,float)
 if not len(x):return [None,None]
 half=(upper-lower)*np.sqrt(np.log(2/alpha)/(2*len(x)))
 return [float(max(lower,x.mean()-half)),float(min(upper,x.mean()+half))]
