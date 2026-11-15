"""Headless PerceptionLab graph runner.

Mimics perceptionlab12.py without a window: loads the host's BaseNode preamble,
imports the node classes a saved workflow needs, applies each node's saved config
the way load_graph() does, restores edge learned_weight and the global coupling
slider, and runs the host scheduler order:
    pre_step() on all nodes -> transfer previous outputs along edges -> step() all.
Signals are multiplied by coupling*learned_weight in set_input (host behaviour);
arrays are passed unscaled (also host behaviour).

usage: python run_graph.py <perceptionlab_root> <workflow.json> <steps> [trace_spec ...]
       trace_spec = "<node_id>:<output_port>"   (records that output every step)
Writes JSON {trace_spec: [values...]} to stdout. Scalar outputs are recorded
as floats; arrays as their mean.
"""
import os, sys, json, io, contextlib, inspect, importlib.util, random
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


def load_host(root):
    main = sys.modules['__main__']
    src = open(os.path.join(root, 'perceptionlab12.py'), encoding='utf-8').read().splitlines()
    end = next(i for i, l in enumerate(src) if l.startswith('# ==================== NODE LOADING SYSTEM'))
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile('\n'.join(src[:end]), 'perceptionlab12_preamble', 'exec'), main.__dict__)
    from PyQt6 import QtWidgets
    main.__dict__['_qapp'] = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    import numpy as np, cv2
    for k, v in {'np': np, 'cv2': cv2, 'os': os}.items():
        setattr(main, k, v)
    return main


def index_classes(root, main, wanted):
    """Import only the node files that define the wanted class names (cheap)."""
    found = {}
    nodes_dir = os.path.join(root, 'nodes')
    for fn in sorted(os.listdir(nodes_dir)):
        if not fn.endswith('.py'):
            continue
        text = open(os.path.join(nodes_dir, fn), encoding='utf-8', errors='replace').read()
        if not any(f'class {w}' in text for w in wanted - set(found)):
            continue
        spec = importlib.util.spec_from_file_location(fn[:-3], os.path.join(nodes_dir, fn))
        mod = importlib.util.module_from_spec(spec)
        mod.__dict__['__main__'] = main
        sys.path.append(root)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                spec.loader.exec_module(mod)
        except Exception as exc:  # the host skips files that fail to import, so do we
            print(f'skip {fn}: {type(exc).__name__}', file=sys.stderr)
            continue
        for name, cls in inspect.getmembers(mod, inspect.isclass):
            if name in wanted and name not in found and issubclass(cls, main.BaseNode):
                found[name] = cls
    return found


def build(root, wf_path, seed=7):
    import numpy as np
    np.random.seed(seed); random.seed(seed)
    main = load_host(root)
    g = json.load(open(wf_path, encoding='utf-8'))
    wanted = {n['class_name'] for n in g['nodes']}
    classes = index_classes(root, main, wanted)
    nodes = {}
    for nd in g['nodes']:
        cls = classes.get(nd['class_name'])
        if cls is None:
            raise SystemExit(f"missing node class {nd['class_name']}")
        with contextlib.redirect_stdout(io.StringIO()):
            sim = cls()
            cfg = nd.get('config', {})
            if callable(getattr(sim, 'set_config_options', None)):
                sim.set_config_options(cfg)
            for k, v in cfg.items():
                if k.startswith('_last_') or k.startswith('_prev_'):
                    continue
                if hasattr(sim, k) and getattr(sim, k, None) != v:
                    setattr(sim, k, v)
        nodes[nd['id']] = sim
    edges = []
    for e in g.get('edges', []):
        src = nodes[e['from_node_id']]
        ptype = (getattr(src, 'outputs', {}) or {}).get(e['from_port'], 'signal')
        edges.append((e['from_node_id'], e['from_port'], e['to_node_id'], e['to_port'], ptype, e.get('learned_weight', 1.0)))
    coupling = g.get('global_settings', {}).get('coupling', 70) / 100.0
    return nodes, edges, coupling


def step(nodes, edges, coupling):
    for n in nodes.values():
        n.pre_step()
    for s, sp, t, tp, ptype, w in edges:
        try:
            v = nodes[s].get_output(sp)
            if v is not None:
                nodes[t].set_input(tp, v, ptype, coupling * w)
        except Exception:
            pass
    for n in nodes.values():
        try:
            n.step()
        except Exception:
            pass


def scalar(v):
    import numpy as np
    if v is None:
        return None
    try:
        a = np.asarray(v, dtype=np.complex128)
        return float(np.real(a).mean()) if a.size else None
    except Exception:
        return None


if __name__ == '__main__':
    root, wf, steps = sys.argv[1], sys.argv[2], int(sys.argv[3])
    specs = sys.argv[4:]
    nodes, edges, coupling = build(root, wf)
    trace = {s: [] for s in specs}
    with contextlib.redirect_stdout(io.StringIO()):
        for _ in range(steps):
            step(nodes, edges, coupling)
            for s in specs:
                nid, port = s.split(':', 1)
                node = nodes.get(int(nid))
                trace[s].append(scalar(node.get_output(port)) if node is not None else None)
    print(json.dumps(trace))
    os._exit(0)
