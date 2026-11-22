# grid-sweeper

**CS-323 Artificial Intelligence — Complex Engineering Problem: Intelligent Vacuum-Cleaning Robot**

A robot in a grid world must clean every dirty cell and return to its charging station.
It **schedules** the cleaning tasks as a constraint satisfaction problem, then **navigates**
between them with graph search.

| Component | Approach |
|---|---|
| Environment | Loaded from `Environment.txt`: grid size, obstacles, dirty cells D1…Dn, charger |
| Scheduling (CSP) | Backtracking with MRV + degree heuristic, LCV ordering and forward checking; precedence, latest-slot and slot-exclusivity constraints from `Schedule.txt` |
| Navigation | Uniform-Cost Search (uninformed) and A\* with Manhattan distance (informed), compared on path cost and nodes expanded |
| Integration | `execute_schedule` visits tasks in schedule order, joins the legs, returns to the charger, and reports failure if a task is unreachable or no schedule exists |

📄 **Report:** [report/CS24045.pdf](report/CS24045.pdf) · 📓 **Notebook:** [notebook/CS24045.ipynb](notebook/CS24045.ipynb)

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate   # Python >= 3.11
pip install -r requirements.txt
jupyter notebook notebook/CS24045.ipynb               # run all cells
```

Run the checks (lint, tests, interface, notebook):

```bash
tools/ci_local.sh
```

## Inputs

| File | Purpose |
|---|---|
| `data/Environment.txt`, `data/Schedule.txt` | Our own test environment and schedule |
| `data/Environment_Sample.txt`, `data/Schedule_Sample.txt` | Sample files from the problem statement |
| `data/Environment_Error.txt`, `data/Schedule_Error.txt` | Failure case: detected and reported |

Formats follow the problem statement exactly; any valid files can be swapped in.

## Repository layout

```
src/cep/      env.py (parsers, grid) · search.py (UCS, A*) · csp.py (solver)
              integrate.py (execute_schedule) · render.py (output) · compare.py
notebook/     CS24045.ipynb (submitted, self-contained notebook) · markdown/ (its text)
report/       CS24045.pdf (project report) · latex/ (report source)
              figures/ · screenshots/ · genai_log.md (AI use log)
tests/        unit and property tests (pytest, hypothesis)
tools/        ci_local.sh · build_notebook.py · gen_env.py (random input generator)
              compare_search.py · fill_rubric.py · repo_inventory.py
docs/         plan, requirements traceability, design decisions, setup; spec/ (frozen)
```

## Documentation

- [Project report (PDF)](report/CS24045.pdf): problem formulation, algorithms, results, testing, discussion
- [Requirements traceability](docs/requirements.md): every spec requirement → test / notebook / report
- [Design decisions](docs/decisions.md): choices where the spec is silent
- [Project plan](docs/plan.md) · [Setup](docs/setup.md) · [Contributor & AI rules](AGENTS.md)

## Team

| Name | Roll no. | Area |
|---|---|---|
| Muhammad Ahmed Qazi | CS-24045 | Environment, integration, rendering, notebook, infrastructure |
| Mujtaba Jawaid Rao | CS-24047 | Graph search, algorithm comparison |
| Huzaifa Hanif | CS-24039 | CSP scheduling |
| Muhammad Ashar Khan | CS-24035 | Testing, input generator, report |

Generative AI use is logged in [report/genai_log.md](report/genai_log.md) and declared in the report.
