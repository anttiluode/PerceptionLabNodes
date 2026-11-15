import os, sys, json, io, contextlib
os.environ['QT_QPA_PLATFORM']='offscreen'
ROOT=sys.argv[1]
main=sys.modules['__main__']
src=open(ROOT+'/perceptionlab12.py',encoding='utf-8').read().splitlines()
with contextlib.redirect_stdout(io.StringIO()):
    end = next(i for i, l in enumerate(src) if l.startswith('# ==================== NODE LOADING SYSTEM'))
    exec(compile('\n'.join(src[:end]),'pre','exec'),main.__dict__)
import importlib.util, numpy as np
spec=importlib.util.spec_from_file_location('scr',ROOT+'/nodes/selfconsistentresonantloopnode.py')
m=importlib.util.module_from_spec(spec); m.__dict__['__main__']=main; spec.loader.exec_module(m)

def angular_fold(img):
    img=img.astype(float); n=img.shape[0]; c=n//2
    y,x=np.mgrid[0:n,0:n]; r=np.hypot(x-c,y-c); th=np.arctan2(y-c,x-c)
    mask=(r>6)&(r<c-4)
    w=img[mask]-img[mask].mean(); t=th[mask]
    p={k:abs(np.sum(w*np.exp(-1j*k*t)))/len(w) for k in range(1,13)}
    tot=sum(p.values())+1e-12
    return {k:round(v/tot,3) for k,v in p.items()}

def run(fb_mode, steps=600, seed=0):
    np.random.seed(seed)
    node=m.SelfConsistentResonanceNode()
    init=node.compute_eigenfrequencies().copy()
    rng=np.random.default_rng(seed)
    aval=[]; prev_eig=None
    for t in range(steps):
        node.pre_step()
        eeg=np.array([8,4,2,1.5,1,0.5])*(1+0.3*rng.standard_normal(6))
        node.set_input('frequency_input',np.abs(eeg).astype(np.float32),'spectrum')
        if fb_mode=='workflow' and prev_eig is not None:
            node.set_input('feedback_modulation',float(prev_eig[0]),'signal')
            node.set_input('feedback_modulation',float(prev_eig[1]),'signal')
        node.step()
        aval.append(int(node.avalanche_count))
        prev_eig=node.get_output('eigenfrequencies')
    eig=node.get_output('eigen_image')
    final=node.compute_eigenfrequencies()
    corr=float(np.corrcoef(np.log1p(init).ravel(),np.log1p(final).ravel())[0,1])
    return {'mode':fb_mode,'total_avalanche_cells':int(sum(aval)),'steps_with_avalanche':int(sum(a>0 for a in aval)),
            'first_feedback_value':None if prev_eig is None else float(prev_eig[0]),
            'corr_final_vs_initial_logFFT':round(corr,4),'fold_power':angular_fold(eig)}
for mode in ('none','workflow'):
    for s in (0,1):
        print(json.dumps(run(mode,seed=s)))
