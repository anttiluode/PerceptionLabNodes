"""Knob test for ONE node file ("the rz_angle lesson", quantum_darwinism.py, Dec 2025).
For every BaseNode class in the file: drive all input ports with deterministic
synthetic data for N steps, record every output; repeat with exactly one port
left unconnected. A port whose removal changes no output (to 1e-9) under this
probe is reported as 'silent under probe' -- NOT proven dead, since thresholds,
regimes or longer horizons could matter. Baseline is run twice; classes whose
two baselines differ are 'nondeterministic' and their ports are not judged.
"""
import os, sys, json, time, inspect, importlib.util, io, contextlib, random
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT, FN, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
main = sys.modules['__main__']
src = open(os.path.join(ROOT, 'perceptionlab12.py'), encoding='utf-8').read().splitlines()
os.chdir(ROOT)
sink = io.StringIO()
with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
    end = next(i for i, l in enumerate(src) if l.startswith('# ==================== NODE LOADING SYSTEM'))
    exec(compile('\n'.join(src[:end]), 'pre', 'exec'), main.__dict__)
from PyQt6 import QtWidgets
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
import numpy as np, cv2
for k, v in {'np': np, 'cv2': cv2, 'os': os}.items():
    setattr(main, k, v)
BaseNode = main.BaseNode
try:
    import torch
except Exception:
    torch = None
out = {'file': FN, 'classes': {}}
try:
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        spec = importlib.util.spec_from_file_location(FN[:-3], os.path.join(ROOT, 'nodes', FN))
        mod = importlib.util.module_from_spec(spec)
        mod.__dict__['__main__'] = main
        sys.path.append(ROOT)
        spec.loader.exec_module(mod)
except BaseException as e:
    out['import'] = f'{type(e).__name__}'
    print(json.dumps(out)); os._exit(0)

SKIP = ('reset', 'trigger', 'save_trigger', 'load_trigger', 'trigger_export', 'clear', 'save', 'load')

def synth(ptype, t, salt):
    rs = np.random.RandomState(1000 + t * 7 + salt)
    if ptype == 'signal' or ptype == 'float':
        return float(0.6 * np.sin(t * 0.21 + salt) + 0.3 * rs.rand())
    if ptype == 'image':
        y, x = np.mgrid[0:64, 0:64]
        return (0.5 + 0.4 * np.sin(x * 0.3 + t * 0.1 + salt) * np.cos(y * 0.2) + 0.1 * rs.rand(64, 64)).astype(np.float32)
    if ptype == 'complex_spectrum':
        return (rs.randn(64, 64) + 1j * rs.randn(64, 64)).astype(np.complex64)
    return (np.abs(np.sin(np.arange(16) * 0.5 + t * 0.1 + salt)) + 0.1 * rs.rand(16)).astype(np.float32)

def fingerprint(v):
    if v is None:
        return None
    try:
        if hasattr(v, 'bits') and hasattr(v, 'width'):
            return ('qimage', v.width(), v.height())
        a = np.asarray(v)
        if a.dtype == object:
            return repr(v)[:200]
        a = np.nan_to_num(a.astype(np.complex128))
        return a
    except BaseException:
        return repr(v)[:200]

def same(a, b):
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        try:
            return a.shape == b.shape and np.allclose(a, b, atol=1e-9, rtol=1e-7)
        except BaseException:
            return False
    return a == b

def run(cls, drop):
    np.random.seed(7); random.seed(7)
    if torch is not None:
        torch.manual_seed(7)
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        node = cls()
        ins = dict(getattr(node, 'inputs', {}) or {})
        outs = list((getattr(node, 'outputs', {}) or {}).keys())
        rec = {}
        for t in range(N):
            node.pre_step()
            for i, (p, ty) in enumerate(ins.items()):
                if p == drop or p.lower() in SKIP:
                    continue
                node.set_input(p, synth(ty, t, i), ty)
            node.step()
            if t >= N - 2:
                for o in outs:
                    try:
                        rec[(t, o)] = fingerprint(node.get_output(o))
                    except BaseException:
                        rec[(t, o)] = 'ERR'
        try:
            node.close()
        except BaseException:
            pass
    return ins, rec

for name, cls in inspect.getmembers(mod, inspect.isclass):
    if not issubclass(cls, BaseNode) or cls is BaseNode or cls.__module__ != mod.__name__:
        continue
    r = {}
    try:
        ins, base = run(cls, None)
        _, base2 = run(cls, None)
    except BaseException as e:
        r['status'] = f'error:{type(e).__name__}'
        out['classes'][name] = r
        continue
    if not base:
        r['status'] = 'no-outputs'
        out['classes'][name] = r
        continue
    if not all(same(base[k], base2.get(k)) for k in base):
        r['status'] = 'nondeterministic'
        r['ports'] = list(ins)
        out['classes'][name] = r
        continue
    r['status'] = 'ok'
    r['ports'] = {}
    for p in ins:
        if p.lower() in SKIP:
            r['ports'][p] = 'not-probed'
            continue
        try:
            _, alt = run(cls, p)
            changed = [o for (t, o) in base if not same(base[(t, o)], alt.get((t, o)))]
            r['ports'][p] = 'affects:' + ','.join(sorted(set(changed))) if changed else 'SILENT'
        except BaseException as e:
            r['ports'][p] = f'error:{type(e).__name__}'
    out['classes'][name] = r
print(json.dumps(out, default=str))
os._exit(0)
