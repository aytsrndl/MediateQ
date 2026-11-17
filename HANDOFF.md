# MediateQ rebuttal handoff

## Baseline and scope

Repository: https://github.com/aytsrndl/MediateQ

`paper-submission` marks the repository baseline supplied for this handoff:
`3d5fe6a6ac5b43fa843659bf430848e4abf67de4` (`Update README`).
It is a stable reference for rebuttal work, not independent verification that this
exact commit generated the submitted results. Create experiment branches from
this baseline; leave the tag fixed. This document is added in a later commit.

The repository implements question mediation, including the primary
`fully_connected` mediator and four topology conditions. It does not include the
paper's complete downstream answer-generation, evaluation, or statistical
analysis pipeline. Obtain the submitted outputs and those separate pipelines
from the authors before planning comparisons against paper tables.

## Setup (Linux/macOS)

```bash
git clone https://github.com/aytsrndl/MediateQ.git
cd MediateQ
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m compileall -q src
python test_topology_visibility.py
python test_fidelity_tiebreak.py
python run_all_questions.py --help
```

On an existing Codex cloud checkout, use `/workspace/MediateQ` and its retained
`.venv`. Each cloud task is isolated; no additional Git worktree is needed.
Run commands from the repository root because dataset and results paths are
relative. Windows setup instructions are in `README.md`.

## Configure a live backend

Copy `.env.example` to `.env` only if `.env` does not already exist. For the
documented primary backend, set these values in that ignored local file:

```dotenv
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
FIDELITY_MODEL=gpt-4.1-mini
```

Supply `OPENAI_API_KEY` securely through the environment or ignored `.env`.
Never commit keys or send them in experiment logs. OpenAI runs require HTTPS
access to `api.openai.com`. Other supported providers are `ollama`, `arc`, and
`hf`; their required variables are listed in `.env.example`. The primary
mediator's fidelity checker uses OpenAI independently of the role-agent backend,
so changing providers does not remove its OpenAI credential requirement.

The paper reports the two model aliases above; dated snapshots were not recorded,
so exact numerical reproduction is not guaranteed. Record actual settings used
for every new experiment. Do not assume the current runner enforces every
generation setting described in the paper.

## First live check

```bash
python run_all_questions.py --level very_low --topology fully_connected --limit 1
```

Check for a printed final revision and a new workbook in `results/` containing
one completed question. The runner catches per-question exceptions and stops;
a successful process exit alone does not prove experiment completion.

## Experiment commands

The dataset has 30 scenarios at each of four literacy levels (120 inputs total).
CLI levels are `very_low`, `inadequate`, `marginal`, and `adequate`.

```bash
# Primary mediator, all 30 very-low-literacy questions
python run_all_questions.py --level very_low --topology fully_connected

# Four topology conditions, same inputs and configured backbone
for topology in independent centralized decentralized hybrid; do
  python run_all_questions.py --level very_low --topology "$topology"
done

# Targeted rerun, for example after an interrupted experiment
python run_all_questions.py --level very_low --topology hybrid --ids 1 5 9
```

Use `--limit 2` for a small pilot before a larger condition. Inspect completion
after each run. There is no automatic resume: identify missing question IDs and
use `--ids`. Do not run identical conditions simultaneously from the same
checkout because output names use timestamps with second precision.

Choose additional experiments based on reviewer requests; no extra experiment
matrix is committed by this handoff. Keep inputs and evaluation procedures
matched across compared conditions, and label new runs separately from submitted
results. Additional model aliases/endpoints and the separate evaluation pipeline
must be confirmed by the team before reproducing the paper's broader comparisons.

## Outputs and reporting

The runner saves progress after each completed question in timestamped Excel
workbooks under `results/`. Workbooks include input and revised questions,
topology, provider/model, Git commit, timestamp, proposals, votes, decision method,
and LLM-call count. `results/` is Git-ignored: pushing code does not share results.

For each experiment, retain the workbook, console log, exact command, dependency
versions (`python -m pip freeze`), fidelity-model setting, expected/completed
question IDs, and a short interpretation in the team's shared results location.
Record `git rev-parse HEAD` and any uncommitted changes; the workbook's Git hash
alone does not capture uncommitted edits. Preserve prior outputs rather than
overwriting them. Include API errors and incomplete cases in the handoff back to
the lead author.

## Validation and remaining handoff items

Cloud onboarding verified Python 3.12.14, pinned dependency installation,
dependency consistency, source compilation, CLI loading, all four topology
visibility tests, all three fidelity control-flow tests, and dataset loading
(30 questions per level). Tests use stand-ins rather than live model calls.
Live generation has not been verified because provider credentials were absent.

Before the lead author leaves, a teammate should:

- Confirm GitHub write access and perform the one-question live check above.
- Locate submitted result workbooks and the downstream evaluation/analysis code.
- Confirm reviewer-driven priorities, budget, owners, and the exact rebuttal
  deadline/time zone with the lead author.
- Agree on a shared output location and reporting channel.

The `paper-submission` tag and this document must be pushed to GitHub before
teammates can fetch them. Repository access and credentials are managed separately.
