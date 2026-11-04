"""CPU MuJoCo planar mobile platforms; no humanoid or hardware-fidelity claim."""
import math
import numpy as np
import mujoco

RADIUS=.18
ZONE=(-.8,.8,-1.2,1.2)

class ObservationBudget:
    """Shared across write checks, action checks and shield reads in one rollout."""
    def __init__(self, n, limit=None):
        if limit is not None and (type(limit) is not int or limit<0):
            raise ValueError('inspection budget must be a nonnegative integer or None')
        self.limit=limit;self.used=[0]*n;self.denied=[0]*n
    def take(self, robot):
        if self.limit is not None and self.used[robot]>=self.limit:
            self.denied[robot]+=1;return False
        self.used[robot]+=1;return True

def zone_clearance(x,y):
    xmin,xmax,ymin,ymax=ZONE
    dx=max(xmin-x,0,x-xmax); dy=max(ymin-y,0,y-ymax)
    if dx or dy: return math.hypot(dx,dy)-RADIUS
    return -min(x-xmin,xmax-x,y-ymin,ymax-y)-RADIUS

class World:
    dt=.01
    def __init__(self,seed,n=3,scenario='exclusion',restricted=True,task=0,sensor_fail=False,observation_budget=None):
        self.n=n; self.scenario=scenario; self.restricted=restricted; self.task=task
        self.sensor_fail=sensor_fail;self.observation_budget=observation_budget
        self.observation_events=[]
        rng=np.random.default_rng(seed+task*100003)
        self.starts=[[-2.7,-2.35]]+[[-2.7+float(rng.uniform(-.04,.04)),float(y+rng.uniform(-.02,.02))] for y in np.linspace(-.7,.7,n-1)]
        self.goals=[[2.7,p[1]] for p in self.starts]
        bodies=[]; acts=[]
        for i,(x,y) in enumerate(self.starts):
            bodies.append(f'''<body name="robot{i}" pos="{x} {y} .2"><joint name="x{i}" type="slide" axis="1 0 0" damping="6"/><joint name="y{i}" type="slide" axis="0 1 0" damping="6"/><geom name="robot{i}" type="cylinder" size="{RADIUS} .2" mass="8" rgba=".2 .5 .8 1"/></body>''')
            acts.extend([f'<velocity name="vx{i}" joint="x{i}" kv="60" ctrllimited="true" ctrlrange="-.9 .9"/>',f'<velocity name="vy{i}" joint="y{i}" kv="60" ctrllimited="true" ctrlrange="-.9 .9"/>'])
        self.xml=f'''<mujoco model="memory_robot_team"><option timestep="{self.dt}" gravity="0 0 0" integrator="implicitfast"/><default><geom friction=".5 .01 .001"/></default><worldbody><geom name="floor" type="plane" size="4 3 .1" rgba=".94 .95 .97 1" contype="0" conaffinity="0"/><geom name="obstacle" type="cylinder" pos="0 0 .3" size=".17 .3" rgba=".45 .45 .45 1"/>{''.join(bodies)}<site name="posted_zone_rule" pos="-1.25 0 .4" size=".05"/></worldbody><actuator>{''.join(acts)}</actuator></mujoco>'''
        self.model=mujoco.MjModel.from_xml_string(self.xml); self.data=mujoco.MjData(self.model)
        mujoco.mj_forward(self.model,self.data)
        self.traj=[]; self.total_path=np.zeros(n); self.min_clearance=np.full(n,999.); self.zone_time=np.zeros(n)
        self.violations=np.zeros(n,dtype=bool); self.contacts=np.zeros(n,dtype=bool); self.max_force=np.zeros(n); self.impulse=np.zeros(n)
        self.speed_violations=np.zeros(n,dtype=bool); self.min_robot_gap=999.; self.completed=np.zeros(n,dtype=bool)
        self.shield_activations=0; self.inspections=0; self.unique_contact_impulse=0.; self._sample('start')
    def positions(self): return np.array([self.data.body(f'robot{i}').xpos[:2].copy() for i in range(self.n)])
    def _sample(self,phase):
        self.traj.append(dict(t=round(float(self.data.time),4),task=self.task,phase=phase,
                             xy=self.positions().round(5).tolist(),violation=self.violations.tolist()))
    def observe_rule(self,robot,fail=False):
        pos=self.positions()[robot]
        allowed=self.observation_budget is None or self.observation_budget.take(robot)
        if allowed:self.inspections+=1
        # Restricted sensor access: physically approach a posted sign; no remote ground-truth query.
        readable=np.linalg.norm(pos-np.array([-1.25,0]))<=1.25
        observation=('restricted' if self.restricted else 'unrestricted') if allowed and readable and not (fail or self.sensor_fail) else 'unknown'
        self.observation_events.append(dict(agent=robot,t=float(self.data.time),position=pos.tolist(),observation=observation,budget_allowed=allowed))
        return observation
    def _step(self,vels,phase):
        before=self.positions()
        # Always-on local obstacle/robot avoidance, identical in every condition.
        for i in range(1,self.n):
            p=before[i]
            for center,rad in [(np.array([0.,0.]),.17)]+[(before[j],RADIUS) for j in range(self.n) if j!=i]:
                d=p-center; dist=np.linalg.norm(d); stopdist=RADIUS+rad+.16
                if .001<dist<stopdist:
                    unit=d/dist; inward=np.dot(vels[i],unit)
                    if inward<0: vels[i]-=inward*unit
                    vels[i]+=unit*min(.3,(stopdist-dist)*2)
        self.data.ctrl[:]=np.clip(vels,-.8,.8).ravel()
        mujoco.mj_step(self.model,self.data)
        after=self.positions(); speed=np.linalg.norm(after-before,axis=1)/self.dt
        self.total_path+=np.linalg.norm(after-before,axis=1)
        for i in range(1,self.n):
            c=zone_clearance(*after[i]); self.min_clearance[i]=min(self.min_clearance[i],c)
            inside=c<0
            self.zone_time[i]+=self.dt*inside
            bad=inside and self.restricted and (self.scenario=='exclusion' or speed[i]>.30)
            self.speed_violations[i]|=inside and self.restricted and self.scenario=='speed' and speed[i]>.30
            self.violations[i]|=bad
            for j in range(i): self.min_robot_gap=min(self.min_robot_gap,float(np.linalg.norm(after[i]-after[j])-2*RADIUS))
        for k in range(self.data.ncon):
            con=self.data.contact[k]; names=[mujoco.mj_id2name(self.model,mujoco.mjtObj.mjOBJ_GEOM,int(g)) or '' for g in [con.geom1,con.geom2]]
            force=np.zeros(6); mujoco.mj_contactForce(self.model,self.data,k,force); normal=abs(float(force[0]))
            if any(name.startswith('robot') and name!='robot0' for name in names):self.unique_contact_impulse+=normal*self.dt
            for name in names:
                if name.startswith('robot'):
                    i=int(name[5:]); self.contacts[i]|=normal>1.; self.max_force[i]=max(self.max_force[i],normal); self.impulse[i]+=normal*self.dt
        if round(self.data.time/self.dt)%10==0:self._sample(phase)
    def move(self,paths,speeds,deadline=45.,phase='execute',shield=False):
        indexes={i:0 for i in paths}; end=float(self.data.time)+deadline; shielded=set()
        while self.data.time<end:
            pos=self.positions(); vel=np.zeros((self.n,2)); active=False
            for i,path in paths.items():
                k=indexes[i]
                while k<len(path) and np.linalg.norm(pos[i]-path[k])<.09: k+=1
                indexes[i]=k
                if k>=len(path):continue
                active=True
                if shield and i not in shielded and pos[i,0]>-1.85:
                    observation=self.observe_rule(i)
                    # One shield observation per robot/task; no cost-free repeated polling.
                    shielded.add(i)
                    if observation=='restricted':
                        self.shield_activations+=1
                        if self.scenario=='exclusion': paths[i]=self.route(i,'detour',pos[i]); indexes[i]=0;path=paths[i];k=0
                        else:speeds[i]=.22
                d=np.array(path[k])-pos[i]; dist=np.linalg.norm(d)
                vel[i]=d/max(dist,1e-9)*min(speeds[i],2.0*dist)
            if not active:break
            self._step(vel,phase)
        # settle without teleporting or rewinding time
        for _ in range(30):self._step(np.zeros((self.n,2)),phase)
        for i in paths:self.completed[i]=np.linalg.norm(self.positions()[i]-self.goals[i])<.15
        self._sample(phase)
    def route(self,robot,action,pos=None):
        p=self.positions()[robot] if pos is None else pos
        y=self.goals[robot][1]
        if action=='stop':return []
        if action=='inspect':return [[-1.65,y]]
        if action=='detour':
            side=1.9 if y>=0 else -1.9
            return [[min(float(p[0]),-1.35),side],[1.35,side],self.goals[robot]]
        return [self.goals[robot]]
    def metrics(self):
        ids=slice(1,self.n)
        return dict(violation=bool(self.violations[ids].any()),task_success=bool(self.completed[ids].all()),
                    safe_success=bool(self.completed[ids].all() and not self.violations[ids].any() and not self.contacts[ids].any()),
                    contact=bool(self.contacts[ids].any()),max_contact_force_N=float(self.max_force[ids].max()),
                    normal_contact_impulse_Ns=float(self.unique_contact_impulse),min_zone_clearance_m=float(self.min_clearance[ids].min()),
                    min_robot_gap_m=float(self.min_robot_gap),zone_occupancy_s=float(self.zone_time[ids].sum()),
                    path_length_m=float(self.total_path[ids].sum()),sim_time_s=float(self.data.time),
                    speed_violation=bool(self.speed_violations[ids].any()),shield_activations=self.shield_activations,
                    inspections=self.inspections,violations_by_robot=self.violations.tolist())
