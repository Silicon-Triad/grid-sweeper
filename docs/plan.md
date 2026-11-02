# Project Plan — CS-323 AI CEP: Intelligent Vacuum-Cleaning Robot

Status: **APPROVED — 2026-11-02** (M. Ahmed Qazi)
Repo: `Silicon-Triad/grid-sweeper` (public)
Source of truth: `docs/spec/` (Problem Description + Grading Rubric PDFs, frozen). The PDFs win any conflict with this plan or `docs/requirements.md`.
Internal finish: **Mon 16 Nov 2026**. Official deadline: 22 Nov 2026 (slack).

---

## 1. Team and ownership

| Member | Roll no. | GitHub | Owns | Rubric |
|---|---|---|---|---|
| Muhammad Ahmed Qazi | CS-24045 | `@Muhammad-Ahmed-Qazi` | infra, CI, `integrate.py`, `render.py`, notebook build + consolidation, schedule parser (in `env.py`), own `Environment.txt`, error files | C3, notebook |
| Mujtaba Jawaid Rao | CS-24047 | `@MujtabaJRao` | `search.py`, algorithm comparison | C1, C4 |
| Huzaifa Hanif | CS-24039 | `@Huzaifa-Hanif-01` | `csp.py` | C2 |
| Muhammad Ashar Khan | CS-24035 | `@MUHAMMD-ASHAR-KHAN` | env parser (`env.py`), `tools/gen_env.py`, `tests/`, report | C5, verification |

Cross-review pairs (each person must be able to explain the other's area at the viva):
- Mujtaba ↔ Huzaifa (search ↔ CSP)
- Qazi ↔ Ashar (integration ↔ tests/env)

Notebook filename: `CS24045.ipynb`.

---

## 2. AI policy (summary — full rules in `AGENTS.md`)

- **AI may:** write/edit `docs/` (except `docs/spec/`), `.github/`, `tools/ci_local.sh`, `tools/build_notebook.py`; create issues, labels, milestones; write PR descriptions; review PRs; run tests and report results.
- **AI may not:** author or edit `src/`, `tests/`, `tools/gen_env.py`, `data/`, solution cells of the notebook, or report prose. Review comments may point at bugs; a human writes the fix.
- **Enforced by:** CI job `ai-boundary` (fails if any commit carrying an AI `Co-Authored-By` trailer touches forbidden paths) + PR template field "Model used".
- **One exception:** the scaffold commit (#1) may create `src/cep/*.py` stubs containing only the frozen signatures, docstrings quoting the spec, and `raise NotImplementedError`. `tests/` and `data/` get `.gitkeep` only. `ai-boundary` is enforced from the commit after the scaffold.
- Every AI use is logged in `report/genai_log.md` → feeds the report's GenAI declaration.

---

## 3. Layout

```
cs323-cep-vacuum-robot/
├── AGENTS.md                # single rulebook (humans + AI)
├── CLAUDE.md                # contains only: @AGENTS.md
├── CONTRIBUTING.md          # short onboarding → AGENTS.md
├── README.md
├── requirements.txt         # pytest, pytest-cov, hypothesis, nbstripout, nbmake, jupyter, matplotlib, ruff
├── pyproject.toml           # ruff + pytest config, package = src/cep
├── docs/
│   ├── spec/                # frozen PDFs + SHA256SUMS
│   ├── requirements.md      # REQ-IDs → spec §, rubric C#, verification
│   ├── plan.md              # this file
│   ├── setup.md             # dev env (Python, venv, Jupyter, nbstripout)
│   └── decisions.md         # design decisions where the spec is silent
├── data/
│   ├── Environment.txt          Schedule.txt           # own
│   ├── Environment_Sample.txt   Schedule_Sample.txt    # from spec
│   └── Environment_Error.txt    Schedule_Error.txt     # failure case
├── src/cep/
│   ├── env.py        # parsers, grid, validation           (Ashar: env parser; Qazi: schedule parser)
│   ├── search.py     # successors, goal, cost, h, search   (Mujtaba)
│   ├── csp.py        # MRV/degree, LCV, FC, backtracking   (Huzaifa)
│   ├── integrate.py  # execute_schedule                    (Qazi)
│   └── render.py     # grid/path/schedule display          (Qazi)
├── tests/
│   ├── fixtures/     # edge-case and invalid input files
│   ├── test_env.py  test_search.py  test_csp.py  test_integrate.py
│   └── test_properties.py   # hypothesis + gen_env
├── notebook/CS24045.ipynb
├── report/
│   ├── figures/  screenshots/
│   └── genai_log.md
├── tools/
│   ├── gen_env.py           # random valid/invalid env + schedule (Ashar)
│   ├── build_notebook.py    # assembles notebook from src/ + md cells (Qazi)
│   └── ci_local.sh          # runs all CI checks locally
└── .github/
    ├── workflows/ci.yml
    ├── CODEOWNERS
    ├── pull_request_template.md
    └── ISSUE_TEMPLATE/{task.yml, spec-question.yml}
```

---

## 4. Frozen interfaces

Change only via an approved issue labelled `frozen-interface`.

**Input formats:** `Environment.txt` (spec §5.2), `Schedule.txt` (spec §6) — exactly as specified.

**Function signatures** (spec §5.5, §6, §7):
```python
get_successors(state, grid) -> list[tuple[state, action, int]]
goal_test(state, goal_state) -> bool
path_cost(path) -> int
heuristic(state, goal_state) -> int
search(grid, start, goal, algorithm) -> (path | None, cost | None, nodes_expanded)

select_unassigned_variable(assignment, domains, constraints)
order_domain_values(variable, assignment, domains, constraints)
is_consistent(variable, value, assignment, constraints) -> bool
forward_check(variable, value, assignment, domains, constraints) -> domains | None
backtracking_search(variables, domains, constraints) -> assignment | None

execute_schedule(grid, charging_station, schedule, algorithm) -> (complete_path, total_cost, success)
```

**Internal types** (fixed in M0, issue #3): `state = (row, col)`; `Grid` structure; `Constraints` structure; algorithm names `"ucs"`, `"astar"`.

---

## 5. Requirement IDs

Full table in `docs/requirements.md` (issue #2). Prefixes:

| Prefix | Spec § | Rubric |
|---|---|---|
| `REQ-ENV-xx` | §5.2, §5.3 (environment file, grid, formulation) | C1 |
| `REQ-SRCH-xx` | §5.4, §5.5 (search functions + requirements) | C1 |
| `REQ-CMP-xx` | §5.4 comparison | C4 |
| `REQ-CSP-xx` | §6 | C2 |
| `REQ-INT-xx` | §7 integration | C3 |
| `REQ-NB-xx` | notebook instructions | all |
| `REQ-TEST-xx` | test runs | C5 |
| `REQ-RPT-xx` | report format + sections | C5 |

Each requirement: one parent spec §, rationale, verification method (`test:<name>`, `notebook:<section>`, or `report:<section>`). Issues, commits, PRs and comments cite IDs.

---

## 6. Milestones

| Milestone | Due | Exit condition |
|---|---|---|
| **M0 Foundation** | Tue 3 Nov | Scaffold merged, CI green, requirements.md approved, parsers + gen_env + test skeletons merged, own/error data files committed |
| **M1 Search** | Fri 6 Nov | UCS + A* pass all search tests incl. edge cases; comparison numbers produced |
| **M2 CSP** | Mon 9 Nov | Solver passes all CSP tests incl. infeasible + unconstrained; constraint proof displayed |
| **M3 Integration** | Wed 11 Nov | `execute_schedule` passes integration + property tests; 3 test runs captured |
| **M4 Submission** | Mon 16 Nov | Notebook runs clean on submitted files; report complete + formatted; print-ready |

Parallelism: after #3 + #5 land (3 Nov), search (M1) and CSP (M2) proceed in parallel; M2 date is a review deadline, not a start date.

---

## 7. Labels

| Group | Labels |
|---|---|
| Area | `env`, `search`, `csp`, `integration`, `notebook`, `report`, `test`, `infra` |
| Type | `feature`, `bug`, `docs` |
| Flags | `spec-question`, `design-decision`, `frozen-interface`, `analysis`, `blocked` |

---

## 8. Workflow

1. One branch per issue: `<issue#>-<short-slug>` (e.g. `12-astar`).
2. Commits cite REQ-IDs: `search: add A* (REQ-SRCH-05) #12`.
3. PR → template filled (issue, REQ-IDs, tests run, model used) → 1 approval from the code owner of every touched area → squash merge.
4. `main` protected by org ruleset: PR required, 1 approval, code-owner review, squash only, no force push/deletion, required checks green.
5. Spec silent? Open a `spec-question` issue. Decision recorded in `docs/decisions.md`, labelled `design-decision` — never presented as a spec value.

### Done checklist (per PR)
- [ ] Cites issue + REQ-IDs
- [ ] `tools/ci_local.sh` passes locally
- [ ] Docstrings on new functions; comments explain *why*
- [ ] No hardcoded paths/coordinates outside `data/` and `tests/fixtures/`
- [ ] Frozen interfaces unchanged (or `frozen-interface` issue approved)
- [ ] "Model used" field filled; AI use logged in `report/genai_log.md`

---

## 9. CI (`.github/workflows/ci.yml`, GitHub-hosted, target < 3 min)

| Job | Checks |
|---|---|
| `lint` | `ruff check`, `ruff format --check`, `nbstripout --verify` |
| `test` | `pytest tests/ --ignore=tests/test_properties.py --cov=src/cep` |
| `robustness` | `pytest tests/test_properties.py` (hypothesis, bounded examples) |
| `interface` | AST check: frozen signatures in `src/cep/` match §4 |
| `notebook` | `build_notebook.py --check` (committed notebook == rebuilt) + `pytest --nbmake notebook/` |
| `traceability` | PR body contains ≥1 `REQ-` ID and a "Model used" line |
| `ai-boundary` | Fails if a commit with AI `Co-Authored-By` trailer touches forbidden paths (§2) |
| `spec-frozen` | `docs/spec/` matches `SHA256SUMS` |

`tools/ci_local.sh` runs the same set (minus `traceability`).

---

## 10. Issues

All unassigned at creation; owner shown for assignment later. All in milestone shown.

### M0 Foundation (due 3 Nov)
| # | Title | Labels | Owner | REQ | Acceptance |
|---|---|---|---|---|---|
| 1 | Scaffold: layout, configs, CI, templates, AGENTS.md | infra | Qazi (AI-assisted) | — | Layout per §3; CI runs green on empty stubs; rulesets applied |
| 2 | Write `docs/requirements.md` from spec | docs | Qazi (AI draft, team approve) | all | Every spec "must" has an ID, parent §, rubric C#, verification method; 4 approvals |
| 3 | Fix internal types: `Grid`, `Constraints`, algorithm names | env, frozen-interface | Ashar | REQ-ENV | Types documented in `env.py` docstring + AGENTS.md; reviewed by all owners |
| 4 | Environment parser + grid | env, feature | Ashar | REQ-ENV | Parses sample; D1…Dn in file order; clean error on malformed/overlapping/out-of-bounds input |
| 5 | Schedule parser + validation | env, feature | Qazi | REQ-CSP | Parses sample; rejects slots < tasks and unknown labels with clear message |
| 6 | `tools/gen_env.py` random env/schedule generator | test, feature | Ashar | REQ-TEST | Flags for size/obstacles/dirt; modes: reachable, unreachable, feasible, infeasible; seeded |
| 7 | Test skeletons + fixtures for all modules | test | Ashar | REQ-SRCH, REQ-CSP, REQ-INT | Tests written from spec, initially xfail; fixtures for start==goal, no path, infeasible, unconstrained |
| 8 | Own `Environment.txt` | env | Qazi | REQ-ENV | ≥8×8, ≥6 obstacles, ≥4 dirty, all reachable, no overlap, ≠ sample |
| 9 | Own `Schedule.txt` | csp | Huzaifa | REQ-CSP | ≥3 precedence, ≥2 latest-slot, feasible, includes ≥1 unconstrained task |
| 10 | Error files `Environment_Error.txt` / `Schedule_Error.txt` | env, test | Qazi | REQ-TEST | Triggers no-path and/or infeasible-schedule path; failure reported cleanly |

### M1 Search (due 6 Nov)
| # | Title | Labels | Owner | REQ | Acceptance |
|---|---|---|---|---|---|
| 11 | `get_successors`, `goal_test`, `path_cost`, `heuristic` | search, feature | Mujtaba | REQ-SRCH | Ashar's unit tests pass; empty + single-state path handled |
| 12 | `search()` — UCS | search, feature | Mujtaba | REQ-SRCH | Optimal path, cost, nodes_expanded; start/goal are inputs |
| 13 | `search()` — A* (Manhattan) | search, feature | Mujtaba | REQ-SRCH | Same cost as UCS on all property-test grids; nodes ≤ UCS |
| 14 | Search edge cases | search | Mujtaba | REQ-SRCH | start==goal → `[start]`, 0; no path → `None` + clear message; paths adjacent + obstacle-free |
| 15 | Heuristic justification (admissible + consistent) | search, docs | Mujtaba | REQ-SRCH | Markdown cell + report paragraph with argument |
| 16 | Algorithm comparison: table + plot + analysis | search, analysis | Mujtaba | REQ-CMP | Path, cost, nodes for both on ≥3 start/goal pairs + scaling over grid sizes; quantitative + qualitative discussion |

### M2 CSP (due 9 Nov)
| # | Title | Labels | Owner | REQ | Acceptance |
|---|---|---|---|---|---|
| 17 | `select_unassigned_variable` (MRV + degree) | csp, feature | Huzaifa | REQ-CSP | Tie-break by degree verified by test |
| 18 | `order_domain_values` (LCV) | csp, feature | Huzaifa | REQ-CSP | Ordering verified by test |
| 19 | `is_consistent` | csp, feature | Huzaifa | REQ-CSP | Precedence, latest-slot, exclusivity each covered |
| 20 | `forward_check` + domain restoration | csp, feature | Huzaifa | REQ-CSP | Empty domain → failure; domains restored on backtrack (test) |
| 21 | `backtracking_search` + infeasible reporting | csp, feature | Huzaifa | REQ-CSP | Vars from all dirty cells incl. unconstrained; infeasible → `None` + message |
| 22 | Schedule display + per-constraint proof | csp | Huzaifa | REQ-CSP | Each constraint printed with ✓/✗ and evidence |

### M3 Integration (due 11 Nov)
| # | Title | Labels | Owner | REQ | Acceptance |
|---|---|---|---|---|---|
| 23 | `execute_schedule` | integration, feature | Qazi | REQ-INT | Start/end at charger; schedule order; no duplicated joints; unreachable → `success=False` |
| 24 | Output + final grid render | integration | Qazi | REQ-INT | Schedule, visit order, per-leg paths, final grid, moves/cost, status |
| 25 | Property tests across modules (hypothesis) | test | Ashar | REQ-TEST | Invariants hold over ≥200 generated cases; runs < 60 s in CI |
| 26 | Three test runs + screenshots | test | Ashar | REQ-TEST | Own, sample, error runs captured for notebook and report |

### M4 Submission (due 16 Nov)
| # | Title | Labels | Owner | REQ | Acceptance |
|---|---|---|---|---|---|
| 27 | `build_notebook.py` + consolidated `CS24045.ipynb` | notebook | Qazi | REQ-NB | Names/roll nos. first cell; markdown per section; runs top-to-bottom on submitted files |
| 28 | Report: formulation, search, CSP, integration sections | report | Section owners; assembled by Ashar | REQ-RPT | Each owner writes own section; pseudocode included |
| 29 | Report: results, testing, discussion | report | Ashar (+ Mujtaba for C4) | REQ-RPT | Completeness/optimality, limitations, improvements |
| 30 | Report: format pass, references, GenAI declaration | report | Ashar | REQ-RPT | TNR 11 pt, headings 12/14 pt, rubric as title page; declaration from `genai_log.md` |
| 31 | Submission checklist | notebook, report | Qazi | REQ-NB, REQ-RPT | `CS24045.ipynb` + PDF + 4 input files on Classroom; double-sided hardcopy ready |

---

## 11. Open items before population

- [ ] Org name + four GitHub usernames (for CODEOWNERS)
- [ ] Team approval of this plan

---

## Changelog

- 2026-11-02: #5, #8, #10 reassigned Ashar → Qazi (M0 load)
