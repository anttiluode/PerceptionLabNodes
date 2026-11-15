"""Headless audit of ONE PerceptionLab node file.
Loads the real host preamble (BaseNode etc. from perceptionlab12.py, everything before the node loader)
as __main__, imports the module the way the host does, instantiates each BaseNode
subclass defined in it, and calls step() N times with no inputs, then again with
simple synthetic inputs on every port. Prints one JSON line.
"""
import os, sys, json, time, inspect, importlib.util, traceback, io, contextlib
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT, FN, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
main = sys.modules['__main__']
src = open(os.path.join(ROOT, 'perceptionlab12.py'), encoding='utf-8').read().splitlines()
end = next(i for i, l in enumerate(src) if l.startswith('# ==================== NODE LOADING SYSTEM'))
pre = '\n'.join(src[:end])
os.chdir(ROOT)
sink = io.StringIO()
with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
    exec(compile(pre, 'perceptionlab12_preamble', 'exec'), main.__dict__)
from PyQt6 import QtWidgets
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
import numpy as np, cv2
BaseNode = main.BaseNode
for k, v in {'BaseNode': BaseNode, 'PA_INSTANCE': main.PA_INSTANCE, 'np': np, 'cv2': cv2, 'os': os}.items():
    setattr(main, k, v)
out = {'file': FN, 'import': None, 'classes': {}}
t0 = time.time()
try:
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        spec = importlib.util.spec_from_file_location(FN[:-3], os.path.join(ROOT, 'nodes', FN))
        mod = importlib.util.module_from_spec(spec)
        mod.__dict__['__main__'] = main
        sys.path.append(ROOT)
        spec.loader.exec_module(mod)
    out['import'] = 'ok'
except BaseException as e:
    out['import'] = f'{type(e).__name__}: {str(e)[:160]}'
    print(json.dumps(out)); sys.exit(0)
out['import_s'] = round(time.time() - t0, 2)

def synth(ptype, t):
    if ptype == 'signal':
        return float(np.sin(t * 0.2))
    if ptype == 'image':
        y, x = np.mgrid[0:64, 0:64]
        return (0.5 + 0.5 * np.sin(x * 0.3 + t * 0.1) * np.cos(y * 0.2)).astype(np.float32)
    if ptype == 'complex_spectrum':
        return (np.random.randn(64, 64) + 1j * np.random.randn(64, 64)).astype(np.complex64)
    return np.abs(np.sin(np.arange(16) * 0.5 + t * 0.1)).astype(np.float32)

for name, cls in inspect.getmembers(mod, inspect.isclass):
    if not issubclass(cls, BaseNode) or cls is BaseNode or cls.__module__ != mod.__name__:
        continue
    rec = {}
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            node = cls()
        rec['init'] = 'ok'
        rec['inputs'] = {k: v for k, v in getattr(node, 'inputs', {}).items()} if isinstance(getattr(node, 'inputs', None), dict) else {}
        rec['outputs'] = {k: v for k, v in getattr(node, 'outputs', {}).items()} if isinstance(getattr(node, 'outputs', None), dict) else {}
    except BaseException as e:
        rec['init'] = f'{type(e).__name__}: {str(e)[:140]}'
        out['classes'][name] = rec
        continue
    for phase in ('empty', 'driven'):
        err = None
        live_outputs = set()
        t1 = time.time()
        try:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                for t in range(N):
                    node.pre_step()
                    if phase == 'driven':
                        for p, ty in rec['inputs'].items():
                            if p.lower() in ('reset', 'trigger', 'save_trigger', 'load_trigger', 'trigger_export', 'clear'):
                                continue
                            node.set_input(p, synth(ty, t), ty)
                    node.step()
                    if t >= N - 3:
                        for o in rec['outputs']:
                            try:
                                v = node.get_output(o)
                            except BaseException:
                                v = None
                            if v is None:
                                continue
                            try:
                                a = np.asarray(v)
                                if a.size and np.all(np.isfinite(np.abs(a.astype(np.complex128)))):
                                    live_outputs.add(o)
                            except BaseException:
                                live_outputs.add(o)
        except BaseException as e:
            tb = traceback.extract_tb(e.__traceback__)
            line = tb[-1].lineno if tb else None
            err = f'{type(e).__name__}: {str(e)[:120]} @L{line}'
        rec[phase] = err or 'ok'
        rec[phase + '_ms_per_step'] = round((time.time() - t1) * 1000 / max(N, 1), 2)
        rec[phase + '_live_outputs'] = sorted(live_outputs)
    try:
        node.close()
    except BaseException:
        pass
    out['classes'][name] = rec
print(json.dumps(out))
os._exit(0)
