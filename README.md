# MediateQ: Multi-Agent Mediation of Low-Health-Literacy Clinical Questions

This repository contains the implementation of **MediateQ**, a multi-agent framework for clarifying ambiguous or low-health-literacy clinical questions before they are passed to a separate language model for answering.

The mediator does **not** generate the clinical answer. Instead, specialized clinical-role agents interpret the patient's intended question, coordinate according to a selected multi-agent topology, and produce a meaning-preserving revised question.

This code accompanies our AAMAS 2027 submission:

**Before the Answer: Multi-Agent Mediation of Low-Health-Literacy Clinical Questions**

## Repository Scope

This repository contains the MediateQ question-mediation implementation, including:

- clinical-role agents
- domain-specific role routing
- the primary fully connected mediation protocol
- four multi-agent coordination topologies
- multiple LLM provider interfaces
- the postpartum question dataset used by the mediator
- topology visibility tests

The downstream answer-generation and evaluation pipeline is treated separately from the mediator implementation.

## Paper-to-Code Mapping

| Paper Component | Implementation |
|---|---|
| Primary MediateQ mediator | `src/topologies/fully_connected.py` |
| Independent topology | `src/topologies/independent.py` |
| Centralized topology | `src/topologies/centralized.py` |
| Decentralized topology | `src/topologies/decentralized.py` |
| Hybrid topology | `src/topologies/hybrid.py` |
| Clinical agent implementation | `src/agent.py` |
| Clinical role routing | `src/role_router.py` |
| Clinical role definitions | `config/roles.py` |
| LLM provider interfaces | `src/llm/` |
| Experiment runner | `run_all_questions.py` |
| Question dataset | `data/questions.xlsx` |
| Topology validation | `test_topology_visibility.py` |

## Multi-Agent Topologies

MediateQ evaluates four coordination structures.

### Independent

Clinical-role agents generate proposals independently without direct peer communication. A separate aggregation stage produces the final revised question.

### Centralized

Agents independently generate candidate revisions. A central orchestrator receives the proposals and selects or synthesizes the final revision.

### Decentralized

Agents first generate independent proposals and then observe peer proposals during a second communication round. Final selection is performed through consensus or voting.

### Hybrid

The hybrid architecture combines central coordination and peer communication. Agents first generate proposals, an orchestrator produces intermediate guidance, agents perform a peer-aware second round, and a final orchestrator produces the revised question.

## Installation

Python 3.12 was used during development.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1