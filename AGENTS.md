# AGENTS.md — rulebook for humans and AI agents

Applies to everyone who changes this repository: team members and any AI tool
(Claude, Copilot, ChatGPT, …). `CLAUDE.md` only imports this file.

Source of truth: `docs/spec/` (Problem Description + Grading Rubric PDFs, frozen).
The PDFs win any conflict with `docs/plan.md`, `docs/requirements.md` or this file.

## Repo map

| Path | Purpose | Owner |
|---|---|---|
| `docs/spec/` | Frozen spec PDFs + `SHA256SUMS`. **Never edit.** | — |
| `docs/plan.md` | Approved project plan | Qazi |
| `docs/requirements.md` | REQ-IDs → spec §, rubric C#, verification | Qazi (team approves) |
| `docs/decisions.md` | Design decisions where the spec is silent | all |
| `docs/setup.md` | Dev environment | Qazi |
| `src/cep/env.py` | Parsers, grid, validation | Ashar (env parser) + Qazi (schedule parser) |
| `src/cep/search.py` | Successors, goal test, cost, heuristic, UCS/A* | Mujtaba |
| `src/cep/csp.py` | MRV/degree, LCV, forward checking, backtracking | Huzaifa |
| `src/cep/integrate.py` | `execute_schedule` | Qazi |
| `src/cep/render.py` | Grid / path / schedule display | Qazi |
| `tests/`, `tests/fixtures/` | Unit + property tests, edge-case input files | Ashar |
| `data/` | `Environment*.txt`, `Schedule*.txt` input files | Qazi (own `Environment.txt`, error files) + Huzaifa (own `Schedule.txt`) |
| `tools/gen_env.py` | Random valid/invalid env + schedule generator | Ashar |
| `tools/build_notebook.py` | Assembles the notebook from `src/` + markdown | Qazi |
| `tools/ci_local.sh` | Runs every CI check locally | Qazi |
| `notebook/CS24045.ipynb` | Submitted notebook (generated) | Qazi |
| `report/` | Report material; `genai_log.md` = AI use log | Ashar |
| `.github/` | CI, CODEOWNERS, PR/issue templates | Qazi + Ashar |

Owners (plan §1): Muhammad Ahmed Qazi `@Muhammad-Ahmed-Qazi` (infra, CI,
integration, render, notebook, schedule parser, own `Environment.txt`,
error files — C3), Mujtaba Jawaid Rao `@MujtabaJRao` (search,
comparison — C1, C4), Huzaifa Hanif `@Huzaifa-Hanif-01` (CSP — C2), Muhammad
Ashar Khan `@MUHAMMD-ASHAR-KHAN` (env parser, generator, tests, report — C5).
Cross-review pairs: Mujtaba ↔ Huzaifa, Qazi ↔ Ashar.

## Commands

```bash
python3 -m venv .venv && source .venv/bin/activate   # Python >= 3.11
pip install -r requirements.txt
nbstripout --install
tools/ci_local.sh                 # all CI jobs except traceability
tools/ci_local.sh lint test       # selected jobs
ruff check . && ruff format .     # lint + autoformat
pytest tests/                     # tests only
python tools/build_notebook.py    # rebuild notebook/CS24045.ipynb
```

## Coding standards

- PEP 8, enforced by `ruff check` and `ruff format` (config in `pyproject.toml`).
- Every public function has a Google-style docstring (Args / Returns).
- Type hints on all new functions (frozen parameter names/order stay unchanged).
- Comments explain *why*, not *what*.
- No hardcoded paths, coordinates, task counts, slots or constraints outside
  `data/` and `tests/fixtures/` (spec §2: "rather than relying on a hardcoded
  environment, number of tasks, time slots, or constraints").

## REQ-ID citation rule

Every issue, commit, PR and code comment that implements or tests a requirement
cites its ID from `docs/requirements.md`
(`REQ-ENV`, `REQ-SRCH`, `REQ-CMP`, `REQ-CSP`, `REQ-INT`, `REQ-NB`, `REQ-TEST`, `REQ-RPT`).
Commit format: `search: add A* (REQ-SRCH-05) #12`.

## Frozen interfaces (plan §4)

Change only via an approved issue labelled `frozen-interface`. CI job `interface`
checks names and parameter order.

Input formats: `Environment.txt` (spec §5.2), `Schedule.txt` (spec §6.3) — exactly as specified.

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

Internal types (fixed in M0, issue #3): `state = (row, col)`; `Grid` structure;
`Constraints` structure; algorithm names `"ucs"`, `"astar"`. Documentation of
`Grid` and `Constraints` is added here by #3.

## Workflow (plan §8)

1. One branch per issue: `<issue#>-<short-slug>` (e.g. `12-astar`).
2. Commits cite REQ-IDs: `search: add A* (REQ-SRCH-05) #12`.
3. PR → template filled (issue, REQ-IDs, tests run, model used) → 1 approval
   from the code owner of every touched area → squash merge.
4. `main` is protected: PR required, 1 approval, code-owner review, squash
   only, no force push/deletion, required checks green.
5. Spec silent? Open a `spec-question` issue. Record the decision in
   `docs/decisions.md`, label `design-decision` — never present it as a spec value.

### Done checklist (per PR)

- [ ] Cites issue + REQ-IDs
- [ ] `tools/ci_local.sh` passes locally
- [ ] Docstrings on new functions; comments explain *why*
- [ ] No hardcoded paths/coordinates outside `data/` and `tests/fixtures/`
- [ ] Frozen interfaces unchanged (or `frozen-interface` issue approved)
- [ ] "Model used" field filled; AI use logged in `report/genai_log.md`

## AI rules (plan §2)

**AI may:** write/edit `docs/` (except `docs/spec/`), `.github/`,
`tools/ci_local.sh`, `tools/build_notebook.py`; create issues, labels,
milestones; write PR descriptions; review PRs; run tests and report results.

**AI may not:** author or edit `src/`, `tests/`, `tools/gen_env.py`, `data/`,
solution cells of the notebook, or report prose. Review comments may point at
bugs; a human writes the fix.

One exception: the scaffold commit (#1) created `src/cep/*.py` stubs containing
only the frozen signatures, docstrings quoting the spec, and
`raise NotImplementedError`. `ai-boundary` is enforced from the commit after it.

Additionally, every AI agent must:

- Stay inside the assigned issue. No drive-by changes, no mass refactors or
  reformatting of files outside the issue's scope.
- Never edit `docs/spec/` (CI job `spec-frozen`).
- Never invent values the spec does not give (sizes, limits, formats, messages,
  tie-breaks…). Open a `spec-question` issue instead.
- Run `tools/ci_local.sh` before claiming a task is done, and report its result
  truthfully.
- State the model used in the PR ("Model used: <model> (for: …)").
- Log every use in `report/genai_log.md` (date, person, tool/model, purpose, issue).
- Mark AI-authored commits with a `Co-Authored-By:` trailer naming the tool —
  this is what `ai-boundary` checks.

## CI (plan §9)

`lint`, `test`, `robustness`, `interface`, `notebook`, `traceability` (PRs only),
`ai-boundary`, `spec-frozen`. Each runs `tools/ci_local.sh <job>`; jobs skip
gracefully while tests or the notebook do not exist yet.
