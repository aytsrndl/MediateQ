# MediateQ

**Multi-Agent Mediation of Low-Health-Literacy Clinical Questions**

MediateQ is a multi-agent framework for clarifying ambiguous or low-health-literacy clinical questions **before** a separate language model generates an answer. Specialized clinical-role agents interpret the patient's request, compare candidate revisions, and produce a clearer question while attempting to preserve the patient's original meaning.

This repository contains the question-mediation implementation accompanying the preprint:

> **Before the Answer: Multi-Agent Mediation of Low-Health-Literacy Clinical Questions**  
> Amal Alamri, Aytunc Sarandal, Katherine Xing, Mengxi Zhang, and Jiaming Cui

## Scope

This repository contains the mediation stage only. MediateQ does not provide a diagnosis or directly answer the clinical question. The downstream answer-generation and evaluation pipeline is separate, and the mediator does not observe downstream answers or evaluator scores while revising a question.

The repository includes:

- domain-specific clinical-role agents
- role routing for infant care, postpartum physical recovery, and postpartum mental health
- the primary two-stage fully connected mediator
- Independent, Centralized, Decentralized, and Hybrid coordination topologies
- a separate semantic-fidelity tie-breaker for unresolved ties in the primary mediator
- configurable LLM backends
- structured experiment logging
- topology and fidelity-control-flow tests

## Paper-to-Code Mapping

| Paper component | Implementation |
|---|---|
| Role-conditioned clinical agents | `src/agent.py`, `src/role_router.py`, `config/roles.py` |
| Primary mediator protocol | `src/topologies/fully_connected.py` |
| Semantic-fidelity tie-breaker | `src/fidelity_checker.py` |
| Independent topology | `src/topologies/independent.py` |
| Centralized topology | `src/topologies/centralized.py` |
| Decentralized topology | `src/topologies/decentralized.py` |
| Hybrid topology | `src/topologies/hybrid.py` |
| Topology factory | `src/topologies/factory.py` |
| Structured schemas | `src/schemas.py` |
| LLM backends | `src/llm/` |
| Dataset loading | `src/dataset_loader.py` |
| Experiment runner | `run_all_questions.py` |
| Topology visibility test | `test_topology_visibility.py` |
| Fidelity tie-break control-flow test | `test_fidelity_tiebreak.py` |

## Coordination Topologies

| Topology | Peer communication | Central orchestrator | Final rule | Nominal calls |
|---|---:|---:|---|---:|
| Independent | No | No | Synthesis | `n + 1` |
| Centralized | No | Yes | Orchestrator | `n + 1` |
| Decentralized | Yes | No | Consensus / vote | `2n–3n` |
| Hybrid | Yes | Yes | Orchestrator | `2n + 2` |

### Primary mediator

The primary MediateQ mediator uses two stages of fully connected deliberation:

1. Each clinical-role agent independently proposes a revision.
2. Each agent receives the first-stage proposals and produces a peer-reviewed candidate.
3. If the normalized second-stage candidates agree, the result is returned by consensus.
4. Otherwise, candidate identities are hidden and the agents vote.
5. If voting remains tied, a separate semantic-fidelity checker selects the most conservative candidate judged to preserve the source meaning.

The fidelity checker only resolves candidate-selection ties. It does not answer the patient's clinical question.

### Independent

Clinical-role agents generate proposals independently. A non-peer aggregation component receives all proposals and produces the final revised question.

### Centralized

Clinical-role agents generate proposals independently. A central orchestrator receives the proposal set and selects or synthesizes the final revision.

### Decentralized

Agents first generate independent proposals and then communicate all-to-all during a peer-review stage. Agreement yields consensus; otherwise, the agents vote over anonymous candidates. Any remaining vote-count tie is resolved deterministically.

This is intentionally different from the primary mediator's separate semantic-fidelity tie-breaker.

### Hybrid

Agents first generate independent proposals. A central orchestrator produces intermediate guidance, agents perform a peer-aware second stage, and a final orchestrator pass produces the revised question.

## Semantic-Fidelity Safeguards

The original patient question remains the authoritative reference throughout mediation. Prompts instruct agents to preserve the original clinical intent and question type while avoiding unsupported additions such as symptoms, timing, severity, causes, medications, diagnoses, or medical history.

When ambiguity remains, the system is instructed to prefer conservative reformulation rather than inventing missing clinical facts.

Structured proposal traces also retain diagnostic fields for meaning preservation, unsupported-information additions, and a short rationale. These fields are model-generated metadata rather than independent validation.

## Repository Structure

```text
.
├── config/
│   └── roles.py
├── data/
│   └── questions.xlsx
├── src/
│   ├── aggregators/
│   ├── llm/
│   ├── topologies/
│   ├── agent.py
│   ├── dataset_loader.py
│   ├── fidelity_checker.py
│   ├── role_router.py
│   └── schemas.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── run_all_questions.py
├── test_fidelity_tiebreak.py
└── test_topology_visibility.py
```

## Installation

Python 3.12 was used during development.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in the variables required for your selected LLM backend in `.env`. Do not commit `.env`.

Example OpenAI configuration:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
FIDELITY_MODEL=gpt-4.1-mini
```

## Running MediateQ

Primary mediator:

```powershell
python run_all_questions.py --level very_low --topology fully_connected
```

RQ3 topology conditions:

```powershell
python run_all_questions.py --level very_low --topology independent
python run_all_questions.py --level very_low --topology centralized
python run_all_questions.py --level very_low --topology decentralized
python run_all_questions.py --level very_low --topology hybrid
```

Run a small subset:

```powershell
python run_all_questions.py --level very_low --topology hybrid --limit 2
```

Run selected question IDs:

```powershell
python run_all_questions.py --level very_low --topology decentralized --ids 1 5 9
```

## Output

Experiment outputs are written to the `results/` directory. The runner records the source question, selected revision, topology, LLM configuration, proposal traces, votes, final decision method, winning candidate, source agents, and LLM-call count.

Progress is saved after each completed question.

## Validation

Compile the source tree:

```powershell
python -m compileall src
```

Validate topology information flow:

```powershell
python test_topology_visibility.py
```

Validate fidelity tie-break control flow without making a live API call:

```powershell
python test_fidelity_tiebreak.py
```

The fidelity test verifies that:

- a primary-mediator vote tie invokes the separate fidelity checker
- a normal primary-mediator majority does not invoke it
- a Decentralized vote tie uses deterministic resolution instead

## Reproducibility Notes

The preprint reports `gpt-4o-mini` for the primary role-agent and aggregation calls and `gpt-4.1-mini` for fidelity checks. Provider aliases rather than dated model snapshots were recorded for those runs. Later reruns may therefore differ if a provider updates the model behind an alias.

The four coordination architectures are task-specific adaptations used to study differences in peer communication and central coordination. They should not be interpreted as exact reproductions of the systems from which the architecture taxonomy was adapted.

## Safety and Intended Use

MediateQ is a research system for studying question mediation. It is not a clinical decision-support system and should not be used as a substitute for professional medical advice, diagnosis, or treatment.

Improved downstream answer quality does not guarantee semantic fidelity. Meaning preservation should be evaluated separately.

## Citation

```bibtex
@article{alamri2026before,
  title={Before the Answer: Multi-Agent Mediation of Low-Health-Literacy Clinical Questions},
  author={Alamri, Amal and Sarandal, Aytunc and Xing, Katherine and Zhang, Mengxi and Cui, Jiaming},
  year={2026},
  note={Preprint}
}
```
