# Headless tools for PerceptionLab

Small scripts used to build the [fossil-bed page](https://anttiluode.github.io/PerceptionLabNodes/). They load the real `BaseNode` code from `perceptionlab12.py` (everything before the node loader), so nodes see the same base class as in the GUI, but no window opens.

Needs the same Python environment as PerceptionLab (PyQt6, numpy, scipy, opencv; torch for the VAE-style nodes). On Windows, run from any folder and pass your PerceptionLab folder as the first argument, for example `E:\DocsHouse\PerceptionLab`.

| Script | What it does |
|---|---|
| `run_graph.py` | Runs a saved workflow headless in the host's order (pre-step → transfer previous outputs → step) and prints chosen outputs per step as JSON. |
| `audit_node.py` | Imports one node file, instantiates every node class, steps it 30× with no inputs and 30× with synthetic inputs, and reports crashes and which outputs are live. |
| `knob_test.py` | For every input of every class: run with all inputs, then with that one input unplugged. If no output changes, the input is *silent under probe* (the `rz_angle` lesson from `quantum_darwinism.py`). |
| `star_replication.py` | Reruns the Self-Consistent Resonance node with and without the feedback wiring saved in `jewishstar.json`. |

Examples:

```
python tools/run_graph.py E:\DocsHouse\PerceptionLab "E:\DocsHouse\PerceptionLab\graph workflows\ecg.json" 600 1:signal_out
python tools/audit_node.py E:\DocsHouse\PerceptionLab coupler.py 30
python tools/knob_test.py E:\DocsHouse\PerceptionLab coupler.py 30
python tools/star_replication.py E:\DocsHouse\PerceptionLab
```

Limits worth keeping in mind: "steps without crashing" says nothing about whether a node is scientifically right; synthetic inputs (16-value spectra, 64×64 images) can trip nodes that expect other shapes; a silent input may matter in a regime the probe did not reach. Webcam, microphone, EEG-file and network nodes run with nothing plugged in.

`run_graph.py` reproduced two known results, which is why it is trusted for the rest: the ECG loop's 59-step period, and the wave-field probe's ~22-frame mean lag.
