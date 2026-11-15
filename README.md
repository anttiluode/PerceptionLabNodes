# A Functional Taxonomy of PerceptionLab Nodes

## Signals, Fields, Memory, Control, and Learning in a Modular Computational Laboratory

**Working technical paper — 14 November 2026**  
**Subject:** [anttiluode/PerceptionLab](https://github.com/anttiluode/PerceptionLab)  
**Status:** Code-grounded architectural analysis, not a peer-reviewed validation study

### Abstract

PerceptionLab is an extensible node-graph laboratory in which source signals, images, spectra, complex-valued representations, persistent dynamical systems, learning rules, and feedback controllers can be connected into experiments. Its repository snapshot contains **466 Python files in `nodes/`**, but this is a module count, not a count of distinct, working node types: several files define multiple node classes and some provide helpers or standalone scripts. The host discovers subclasses of `BaseNode`, sorts them using author-declared `NODE_CATEGORY` labels, and advances connected graphs in discrete processing steps. This paper proposes a more rigorous, **functional taxonomy of fourteen node classes**, crossing computational role with temporal behavior and representational type. It then compares several kinds of memory, analyses the host's causal semantics, reviews a documented propagation-delay calibration, and identifies specific interface mismatches that limit scientific interpretation. The central claim is methodological: the strongest use of PerceptionLab is not to assert that a vivid visualization constitutes intelligence, consciousness, or physics, but to build controlled experiments that locate where a system's state, prediction, causal delay, and adaptive change actually reside.

**Keywords:** node-based simulation; dynamical systems; signal processing; recurrent memory; phase; propagation; predictive coding; causal intervention; reproducibility.

## 1. Scope and method

This survey inspects the repository's default-branch file tree, the current `perceptionlab12.py` host, representative implementations spanning source and stateful node families, saved graph workflows, and two in-repository experimental notes. The file inventory is broad; the code audit is selective. Accordingly, the proposed taxonomy classifies **architectural families**, not every one of the 466 Python files individually. No full GUI run, package-by-package import audit, or reproducibility sweep was performed for this paper.

Two different meanings of **class** must be kept separate. A *Python node class* is a subclass of `BaseNode` found by reflection; one source file may contain many. A *functional node class* is the scientific role and update mechanism assigned here. The existing `NODE_CATEGORY` field helps place nodes in menus; it is neither a unique ontology nor a guarantee of operational correctness. For example, an oscillator can also be a source, and a cortical model may simultaneously store memory, learn, and control a field.

## 2. The common computational contract

In the latest inspected host, every ordinary node exposes a port declaration, an input collection, a `step()` transition, and a `get_output()` readout. Stateful nodes also retain internal variables, while some save custom persistent state. The essential abstraction is:

> **State update:** xᵢ[t+1] = Fᵢ(xᵢ[t], uᵢ[t]; θᵢ[t])  
> **Readout:** yᵢ[t] = Gᵢ(xᵢ[t]; θᵢ[t])  
> **Learning, when present:** θᵢ[t+1] = θᵢ[t] + Δᵢ(xᵢ[t], uᵢ[t], error[t]).

Here **x** is transient dynamical state, **θ** is a parameter or learned structure, and **u** is input transferred across edges. The distinction between x and θ matters: a memory that survives because an oscillator is still cycling is different from one retained in a learned weight, an archive, or spatial morphology.

The host's core loop first clears per-tick input queues, then transfers available **previous-step outputs** along edges, then runs the nodes' `step()` methods. Thus ordinary host-mediated feedback has at least one discrete tick of causal separation; visual graph cycles are not simultaneous algebraic equations. Four documented port types are `signal`, `image`, `spectrum`, and `complex_spectrum`. The types express broad representations, not full contracts for dimensions, units, sample rates, complex conventions, or spatial alignment. [Host source](https://github.com/anttiluode/PerceptionLab/blob/main/perceptionlab12.py#L87-L164), [scheduler](https://github.com/anttiluode/PerceptionLab/blob/main/perceptionlab12.py#L1178-L1240).

## 3. Fourteen functional classes

The taxonomy below uses **primary role** as the first sorting principle. Multi-functional nodes may belong to more than one class; such overlap should be recorded explicitly, not erased.

| Class | Computational role | Representative source modules |
|---|---|---|
| **I. Sources and perturbation generators** | Introduce recorded, live, synthetic, or experimentally timed input | `media_source.py`, `EDF_EEG_loader.py`, `audiofilesourcenode.py`, `pulsesourcenode.py`, `noise_generator.py` |
| **II. Representation bridges** | Change data type, shape, resolution, or routing | `imagetovectornode.py`, `vectorconverter.py`, `vectorsplitternode.py`, `dimensionadapternode.py`, `imagetocomplexadapter.py` |
| **III. Signal and feature transforms** | Extract frequency, scale, orientation, motion, or low-dimensional features | `fft_cochlea.py`, `wavelet_decompose.py`, `classgaborfilternode.py`, `opticalflownode.py`, `pcanode.py` |
| **IV. Oscillators and phase systems** | Generate or measure rhythm, resonance, phase relation, and cross-frequency coupling | `nestedoscillatornode.py`, `signaloscillatornode.py`, `phasecouplingnode.py`, `septumpacemakernode.py`, `thetabetagatingnode.py` |
| **V. Continuous and propagating fields** | Evolve distributed spatial state by diffusion, reaction, or finite-speed propagation | `livingcheckerboardnode.py`, `wavefieldnode.py`, `reaction_diffusion_node.py`, `ephaptic_field_node.py`, `chaoticfieldnode.py` |
| **VI. Neuronal and cortical models** | Simulate spiking, dendritic gating, cortical organization, or neural population interactions | `geometric_neuron_node.py`, `dendriticwebnode.py`, `thalamicgatenode.py`, `corticalsheetnode.py`, `complexcorticalstacknode.py` |
| **VII. Memory, latches, and attractors** | Retain past input in recurrence, traces, templates, or discrete archival decisions | `moebiusloopmemorynode.py`, `patternmemorybanknode.py`, `attentionlatch.py`, `islandarchivalnode_v2.py`, `mycelialcortexnode.py` |
| **VIII. Learning and predictive inference** | Modify parameters or templates, decode latent state, or predict future observations | `hebbianlearnernode2.py`, `perceptronlayernode.py`, `realvaenode.py`, `predictivecortexnode.py`, `cortical_learning.py` |
| **IX. Regulation, energetic control, and gates** | Stabilize, inhibit, allocate resources, or conditionally route activity | `coupler.py`, `homeostaticregulatornode2.py`, `atpmetabolismnode.py`, `metabolicspikenode.py`, `decisiongatenode.py` |
| **X. Eigenmode, complex, and holographic operators** | Represent structure in modes, complex spectra, interference patterns, and reconstruction maps | `eigenmodeanalysisnode.py`, `modeinterferencenode.py`, `holographicfft.py`, `holographicinterference.py`, `holographicreconstruction.py` |
| **XI. Formal and quantum-inspired models** | Explore algebraic, topological, qubit-like, or measurement-like constructions | `BlochQubitNode.py`, `su2.py`, `su3.py`, `topologicalxornode.py`, `quantumstatetomographynode.py` |
| **XII. Morphogenesis, organisms, and evolution** | Let rules generate shapes, worlds, populations, or evolving structures | `morphogenesisworld.py`, `livingcrystalnode.py`, `autonomousorganismnode.py`, `ecosystemnode.py`, `molecularnodes.py` |
| **XIII. Scientific instruments and probes** | Measure behavior without necessarily changing the simulated system | `temporalmultiscopenode.py`, `coherencemonitornode.py`, `ksweepanalysisnode.py`, `decoherenceratemonitor.py`, `gatevalidatornode.py` |
| **XIV. Rendering, export, and actuation** | Turn internal variables into visual, audible, or recorded outputs | `display_nodes.py`, `signalplotternode.py`, `speaker_output.py`, `spectralsynthnode.py`, `debugdataexporternode.py` |

**The scientific distinction:** a node named “analyzer” can influence the model if its measured output is wired back; a node named “generator” can become an observer if its field is driven only by an external state. Roles describe **what a node does in a particular graph**, not merely what its filename says.

## 4. A second classification: time and memory

The more revealing axis is temporal behavior. Four architectures can look similar on screen while performing fundamentally different computations.

| Temporal mechanism | Minimal form | Interpretation and examples |
|---|---|---|
| **Memoryless transformation** | y[t] = f(u[t]) | Frequency and image transforms convert present input without independently preserving past state (`fft_cochlea`, many adapters). |
| **Leaky trace / filter** | x[t+1] = αx[t] + (1−α)u[t] | A finite-duration history creates persistence but not necessarily order-sensitive memory (`temporalblur`). |
| **Recurrent dynamical memory** | x[t+1] = φ(Rx[t] + Bu[t] + gate[t]) | A circulating or contractive state can retain order and context (`loopmemory`, `moebiusloopmemorynode`, some oscillators). |
| **Spatially distributed causal history** | field[t+1] depends on local field, velocity, and neighbors | Past events occupy different locations or stages of propagation (`wavefieldnode`). |
| **Plastic or structural memory** | θ[t+1] = θ[t] + update | The system alters templates, transitions, weights, or geometry (`mycelialcortexnode`, `predictivecortexnode`, `cortical_learning`). |
| **Conditional archival memory** | x or θ freezes or changes regime when a threshold is crossed | Memory is retained by a gating event rather than continuous replay (`islandarchivalnode_v2`). |

The same node may span rows. `MycelialCortexNode`, for example, maintains a recurrent shared field **and** a set of learned templates. `PredictiveCortexNode` adds an explicitly asymmetric transition table T, so *which pattern followed which* becomes a separately identifiable memory variable. Its source computes a prediction from the preceding winning pattern before it processes the new observation, and exports the resulting surprise residual. This is more specific than saying it “has memory.” [Mycelial source](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/mycelialcortexnode.py), [predictive source](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/predictivecortexnode.py#L133-L210).

One should therefore ask of every stateful node: **What changes? What persists? How can that state be read? How can it be selectively erased? And what happens if it is transplanted into an otherwise identical copy of the system?** These questions are stronger than inspection of an attractive trajectory.

## 5. Causal architecture: why controllers, media, and observers must stay distinct

A productive experimental graph can be decomposed into five parts:

1. **Medium/state:** the evolving field, oscillator, attractor, or learned parameterization.
2. **Write interface:** the location and manner in which an intervention enters it.
3. **Read interface:** the spatial, spectral, or temporal projection that makes state observable.
4. **Propagation/update law:** what determines how an event spreads, decays, or recurs.
5. **Controller and instrument:** what acts on the readout, and what measures the result.

Consider a loop: `PulseSource → WaveField → TemporalMultiScope`, with an optional `WaveField.read_3 → HomeostaticCoupler → WaveField.write_0` return path. The source creates an event, the field carries it, the scope measures causal separation, and the controller can alter the subsequent field trajectory. Combining these into one undifferentiated “intelligent field” would make it impossible to attribute a successful effect to a particular mechanism.

In a general graph, distinguish **passive observation** from **closed-loop feedback**, and **fast state** from **slow learning**. The correct causal experiment freezes or swaps these factors one at a time while keeping all other conditions matched.

## 6. Case study: a calibrated temporal-field experiment

The repository's clearest documented known-answer test compares two field mechanisms. The first-order `LivingCheckerboardNode` follows a relaxation-like equation, approximately `dF/dt = D∇²F − γF + drive`. It can have persistent state yet settle into a nearly shared, zero-lag mode. The second-order `WaveFieldNode` evolves **field and velocity**, approximately `d²F/dt² = c²∇²F − γdF/dt + drive`, allowing a localized pulse to move through successive read apertures.

The code computes a discrete Laplacian, advances velocity and field over substeps, reads local averages, and reports field energy. The `TemporalMultiScopeNode` separately estimates activity, saturation, zero-lag correlation, and lag-optimized cross-correlation; flat channels are excluded from live-channel correlation. This makes it a measuring instrument, not simply another animated display. [Wave field](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/wavefieldnode.py#L173-L218), [scope](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/temporalmultiscopenode.py#L99-L189).

The repository records a predicted **13.2 frames per adjacent aperture gap**. For four equally spaced probes, the six unordered pairs span an average of 10/6 gaps; expected mean absolute lag is therefore **13.2 × 10/6 = 22.0 frames**. The August 2026 notes report manual measurements around **21.3, 21.5, and 22.2 frames**. Those observations support a narrow calibration claim: the field geometry and lag measurement agree in that configuration. They do **not** establish a biological theory of temporal perception. [Calibration note](https://github.com/anttiluode/PerceptionLab/blob/main/docs/TEMPORAL_THICKNESS_CALIBRATION.md), [clean workflow](https://github.com/anttiluode/PerceptionLab/blob/main/graph%20workflows/wave_field_probe.json).

The lesson is precise: **persistence is not the same as distinguishable causal ages**. A field can be stateful yet synchronize into one common mode; a propagating medium can contain multiple observable stages of one past event in the same present snapshot.

## 7. Case study: explicit memory versus apparent memory

`MoebiusTemporalMemoryNode` is an adapter for `LoopMemory`, a numerical recurrent machine rather than a modeled biological neuron. It projects a 256-value input to 16 dimensions and advances a signed-shift recurrence with bounded nonlinear context modulation:

> s[t+1] = tanh(λRs[t] + Bu[t] + g(Bu[t]) ⊙ tanh(ARs[t])).

This provides a controllable comparison among recurrence geometries, leak, input novelty, and erased history. The repository's ECG/Moebius note specifically calls for controls that separate sensory information supplied externally from oscillations generated by an existing feedback loop. Without those controls, an internally sustained beat could be mistaken for an external memory. [Adapter](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/moebiusloopmemorynode.py), [recurrence](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/loopmemory.py), [ECG note](https://github.com/anttiluode/PerceptionLab/blob/main/docs/ECG_MOEBIUS_CONCERTO.md).

By contrast, `PredictiveCortexNode` separates stored **content templates** from a stored **transition relation**. This separation is a valuable architectural pattern: the memory of what was encountered and the memory of what followed it can be independently ablated. A good test would train the same patterns in A→B and B→A order, keep the learned templates fixed, swap only the transition matrices, and ask whether next-state prediction and surprise reverse accordingly.

## 8. Learning systems are not one class of intelligence

The repository contains several distinct learning mechanisms. A Hebbian learner changes associations according to co-activation or an error-modulated local rule. A multilayer perceptron changes numerical weights using supervised targets. `RealVAENode` trains an encoder/decoder latent model on images. `TokenQKVNode` constructs token embeddings and calculates query-key scores, while `NeuralTransformerNode` integrates EEG-oriented token and phase operations. `cortical_learning.py` contains **six** PerceptionLab subclasses, separating substrate, resonant processing, predictive coding, geometry learning, stimulus generation, and monitoring. The saved `cortical_learning_eeg6.json` graph connects 14 node instances with 29 edges, illustrating that learning is intended to occur across differentiated modules rather than within a single black box.

These mechanisms should not be compared using a single metric called “intelligence.” Supervised prediction needs held-out target accuracy; associative memory needs partial-cue recall and false-positive rates; adaptive controllers need stability and effort; a generative model needs reconstruction or generalization tests; and a predictive cortex needs sequence forecasts against baselines. Published attention and associative-memory models are useful conceptual comparators, not proof that the corresponding experimental nodes achieve their performance. [Cortical system](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/cortical_learning.py), [EEG graph](https://github.com/anttiluode/PerceptionLab/blob/main/graph%20workflows/cortical_learning_eeg6.json).

## 9. Interpretive boundaries and code-level audit findings

Scientific labels should follow implemented measurements, not precede them. A module called `EntanglementDetectorNode` computes conventional correlations, histogram mutual information, and a covariance-derived score on input arrays. That can be useful for coupled-signal analysis, but **classical correlation does not establish quantum entanglement**; its `concurrence` quantity is not by itself an experimentally verified quantum-state concurrence. Likewise, `QuantumStateTomographyNode` performs a simplified projection/reconstruction procedure, not a complete physical tomography protocol. A class or menu label such as “Consciousness” is a research hypothesis, not a consciousness detector validated against ground truth. [Detector](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/entanglementdetectornode.py#L56-L141), [tomography](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/quantumstatetomographynode.py#L45-L132).

Source inspection also reveals **testable implementation cautions**:

- **Edge weights are type-dependent.** In the inspected host, scalar `signal` inputs are multiplied by global coupling and learned edge weight. `image`, `spectrum`, and `complex_spectrum` inputs are appended without that multiplication. A weighted-array experiment cannot assume the graphical weight changed the array's numerical amplitude.
- **A declared control may be inactive.** In `coupler.py`, `step()` calculates `effective_gain` from `gain_mod`, but the regulation functions multiply by `self.gain`, not by the calculated value. Thus a graph connected only through `gain_mod` should not be credited with an active gain-modulation effect until this is fixed and retested.
- **An attention interface has a contract mismatch.** `TokenQKVNode.step()` reads `self.inputs`, which the host uses as **port-type declarations**, instead of reading transferred runtime values via `get_blended_input()`. Its sanitizer therefore receives strings such as `"spectrum"` and may produce empty token streams. Moreover, its context-vector formula scales the *sum of values* by a global match score rather than implementing the usual attention-weighted sum over aligned values. It is an attention-inspired demonstrator, not a validated standard QKV implementation.
- **A training-disable signal is currently unreliable.** `PerceptronLayerNode` sets `train_sig = get_blended_input(...) or 1.0`; an explicitly supplied zero is therefore replaced with 1.0. A zero signal does not reliably freeze learning.
- **Loadability is not inferred from filenames.** Dynamic module import can fail on missing packages or incompatible code, and the registry keys classes by name. Duplicate class names from different modules can overwrite earlier entries. The 466 files cannot be equated with 466 operational palette entries.

These are **static-code observations**, not an exhaustive bug report or measured failure rates. They matter because a null or positive scientific result can be dominated by an inactive control path rather than by the hypothesis under test. [Host data handling](https://github.com/anttiluode/PerceptionLab/blob/main/perceptionlab12.py#L101-L155), [edge transfer](https://github.com/anttiluode/PerceptionLab/blob/main/perceptionlab12.py#L1178-L1240), [coupler](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/coupler.py#L182-L225), [QKV node](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/tokenqkvnode.py#L129-L193), [perceptron](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/perceptronlayernode.py#L101-L113).

## 10. A proposed validation framework

A reusable experiment standard should attach **six tests** to every family of nodes:

1. **Contract test.** Supply a known input of the correct type, shape, unit, and range; check actual output and inactive controls. For graphs with learning, verify that the declared freeze input really freezes weights.
2. **Known-answer test.** Choose a regime whose output can be computed independently: a sinusoid for spectral nodes, a stable fixed point for homeostatic control, a propagation lag for wave nodes, or an XOR truth table for logic nodes.
3. **Matched negative control.** Replace the proposed mechanism with a simpler one: stationary field versus traveling wave, shuffled order versus ordered sequence, learned coupling versus fixed weight, genuine sensor versus zero drive.
4. **Causal intervention.** Save and restore fast state, learned parameters, geometry, and controller memory independently. State-swapping is especially useful for locating the *substrate* of an apparent memory.
5. **Readout and generalization test.** Train a readout on one set of trajectories, test on unseen seeds and inputs, and compare against simple delay-line, moving-average, linear, and shuffled baselines.
6. **Reproducibility test.** Record random seed, graph JSON, host revision, dependencies, physical/virtual timestep, device, configuration, and per-run numerical data rather than relying only on screenshots.

A five-level **evidence label** is practical: **E0** code present but unverified; **E1** unit/contract tested; **E2** known-answer calibration; **E3** ablation and matched controls across seeds; **E4** held-out generalization, robust replication, or validated physical measurements. Labels must belong to an exact node version and test, not to an entire project name.

## 11. Recommendations for the node library

Preserve the experimental freedom of the current toolkit, but give each loadable class additional machine-readable metadata: `primary_role`, `secondary_roles`, `port_schema` (dtype, shape, units), `time_model` (memoryless, first-order, second-order, recurrent, plastic), `state_variables`, `parameter_variables`, `reset_behavior`, `determinism_and_seed`, `dependencies`, `evidence_level`, and `known_answer_workflow`. A generated registry could then separate **source file**, **Python class**, **functional family**, and **tested release**.

Three practical changes would immediately improve the science: (i) add a test harness that imports every Python module and records the *actual* loadable subclasses; (ii) route all runtime data through a single typed read/write API so that images, complex arrays, and scalars obey explicit edge-weight rules; and (iii) ship the temporal-wave calibration, an attention contract test, and a training-freeze test as standard smoke experiments.

PerceptionLab's most consequential experiments will be cross-family ones: a sensory stream drives a field; the field offers distinct causal ages; a controller samples it; a predictive memory learns changes in the sampled state; and an observer verifies whether information survives when one of those components is independently replaced. The scientific question becomes **which physical or numerical variable carries the effect**, not which assembled diagram looks most brain-like.

## 12. Conclusion

PerceptionLab is best understood as a **compositional laboratory for causal computation**. Its node modules range from ordinary signal filters and renderers to dynamical media, neuronal analogies, memory machines, learning systems, and formal or quantum-inspired explorations. A useful taxonomy must distinguish their input/output representation, state update, persistence mechanism, learning rule, intervention points, and evidence maturity. The documented wave-field calibration demonstrates the value of that approach: it separates mere persistence from measurable travel time and checks the instrument against a prediction. Similar controls can turn the broader collection from a large creative palette into a structured experimental platform in which claims about memory, resonance, prediction, and control become falsifiable.

## References and source material

**Primary PerceptionLab sources**

- [Repository and README](https://github.com/anttiluode/PerceptionLab); [current inspected host](https://github.com/anttiluode/PerceptionLab/blob/main/perceptionlab12.py).
- [Temporal thickness calibration](https://github.com/anttiluode/PerceptionLab/blob/main/docs/TEMPORAL_THICKNESS_CALIBRATION.md); [ECG + Moebius experiment note](https://github.com/anttiluode/PerceptionLab/blob/main/docs/ECG_MOEBIUS_CONCERTO.md).
- [WaveFieldNode](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/wavefieldnode.py); [TemporalMultiScopeNode](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/temporalmultiscopenode.py); [MycelialCortexNode](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/mycelialcortexnode.py); [PredictiveCortexNode](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/predictivecortexnode.py); [LoopMemory](https://github.com/anttiluode/PerceptionLab/blob/main/nodes/loopmemory.py).

**Background comparisons (not validations of PerceptionLab)**

- Hopfield, J. J. (1982). “Neural networks and physical systems with emergent collective computational abilities.” *PNAS*, 79, 2554–2558. https://doi.org/10.1073/pnas.79.8.2554
- Vaswani, A. et al. (2017). “Attention Is All You Need.” *NeurIPS*. https://arxiv.org/abs/1706.03762
- Turing, A. M. (1952). “The Chemical Basis of Morphogenesis.” *Philosophical Transactions of the Royal Society B*. https://doi.org/10.1098/rstb.1952.0012
- Still, S., Sivak, D. A., Bell, A. J., and Crooks, G. E. (2012). “Thermodynamics of Prediction.” *Physical Review Letters*, 109, 120604. https://doi.org/10.1103/PhysRevLett.109.120604
