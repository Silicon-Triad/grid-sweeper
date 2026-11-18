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
| `src/cep/env.py` | Parsers, grid, validation | Qazi (types, env + schedule parsers); Huzaifa reviews schedule-parser changes |
| `src/cep/search.py` | Successors, goal test, cost, heuristic, UCS/A* | Mujtaba |
| `src/cep/csp.py` | MRV/degree, LCV, forward checking, backtracking | Huzaifa |
| `src/cep/integrate.py` | `execute_schedule` | Qazi |
| `src/cep/render.py` | Grid / path / schedule display | Qazi |
| `tests/`, `tests/fixtures/` | Unit + property tests, edge-case input files | Ashar |
| `data/` | `Environment*.txt`, `Schedule*.txt` input files | Qazi (own `Environment.txt`, own `Schedule.txt`, error files, sample files); matches CODEOWNERS |
| `tools/gen_env.py` | Random valid/invalid env + schedule generator | Ashar |
| `tools/build_notebook.py` | Assembles the notebook from `src/` + markdown | Qazi |
| `tools/ci_local.sh` | Runs every CI check locally | Qazi |
| `notebook/CS24045.ipynb` | Submitted notebook (generated) | Qazi |
| `report/` | Report material; `genai_log.md` = AI use log | Ashar |
| `.github/` | CI, CODEOWNERS, PR/issue templates | Qazi + Ashar |

Owners (plan §1): Muhammad Ahmed Qazi `@Muhammad-Ahmed-Qazi` (infra, CI,
integration, render, notebook, `env.py` types + env/schedule parsers,
own `Environment.txt` + `Schedule.txt`, error files — C3), Mujtaba Jawaid Rao `@MujtabaJRao` (search,
comparison — C1, C4), Huzaifa Hanif `@Huzaifa-Hanif-01` (CSP — C2), Muhammad
Ashar Khan `@MUHAMMAD-ASHAR-KHAN` (generator, tests, report only — C5).
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

### Internal types (issue #3, DEC-06; defined in `src/cep/env.py`)

| Type | Definition | Used by |
|---|---|---|
| `state` | `tuple[int, int]` = `(row, col)`, zero-based, top-left `(0,0)` (REQ-ENV-03) | search, integrate |
| action | string from `ACTIONS` = `UP, DOWN, LEFT, RIGHT` with `(dr, dc)`; this order = successor order = UCS/A* tie-break (REQ-SRCH-02) | search |
| task label | `str` `"D1"…"Dn"`, numbered in file order (REQ-ENV-04) | env, csp, integrate |
| slot | `int` `1…n`; shown as `T<n>` only in output. Never compare labels/slots as strings (`"T10" < "T9"`). | csp, integrate, render |
| algorithm | `ALGORITHMS` = `"ucs"`, `"astar"` (DEC-01); any other name → `search` raises `ValueError` | search, integrate |

**`Grid`** — frozen dataclass (immutable; integration tracks cleaned cells itself):

| Field | Type | Meaning |
|---|---|---|
| `rows`, `cols` | `int` | grid dimensions (line 1) |
| `obstacles` | `frozenset[state]` | blocked cells (line 3) |
| `dirty` | read-only `Mapping[str, state]` (`MappingProxyType`), file order | label → cell (line 5) |
| `charger` | `state` | charging station (line 6) |

Free cells = in-bounds cells not in `obstacles`; dirty and charger cells are
passable. `get_successors` excludes only out-of-bounds and obstacle cells.

**`Constraints`** — frozen dataclass:

| Field | Type | Meaning |
|---|---|---|
| `variables` | `tuple[str, ...]` | all task labels in file order (from `Grid.dirty`), incl. unconstrained (REQ-CSP-03); DEC-05 tie-break order |
| `num_slots` | `int` | available slots (line 1) |
| `precedence` | `tuple[tuple[str, str], ...]` | `(before, after)` pairs (REQ-CSP-05) |
| `latest` | read-only `Mapping[str, int]` (`MappingProxyType`) | label → latest slot (REQ-CSP-06) |

Slot exclusivity is implicit (REQ-CSP-07). Initial `domains` = `initial_domains(constraints)`:
`dict[str, list[int]]`, every variable → `[1…num_slots]` ascending (REQ-CSP-04). `assignment`: `dict[str, int]`.
`execute_schedule`'s `schedule`: `list[str]` of labels in slot order; it converts
them to cells via `grid.dirty`.

## Workflow (plan §8)

1. One branch per issue: `<issue#>-<short-slug>` (e.g. `12-astar`).
2. Commits cite REQ-IDs: `search: add A* (REQ-SRCH-05) #12`.
3. PR → template filled (issue, REQ-IDs, tests run, model used) → 1 approval
   from the code owner of every touched area → squash merge. Exception
   (project-lead decision, 18 Nov): the lead's (Qazi's) PRs need no other
   member's approval; required CI checks must still be green before merge.
4. `main` is protected: PR required, 1 approval, code-owner review (not for
   the lead's PRs, see 3), squash only, no force push/deletion, required checks green.
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

**AI may** author or edit any path **except `docs/spec/`**: `src/`, `tests/`,
`tools/`, `data/`, notebook cells, docs, `.github/`, and report material.
AI may also create issues, labels and milestones, write PR descriptions, review
PRs, run tests and report results. (Changed 2026-11-18, #44: the earlier
restriction on AI-authored code was lifted by team decision under time pressure.)

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
  `ai-boundary` uses it to check that no AI commit touches `docs/spec/`.

Humans who use AI must:

- Be able to explain every line of an AI-authored PR they open or merge — at the
  viva, C6 is graded individually.
- Declare AI-written report prose (in `report/genai_log.md` and the report's
  Generative AI declaration).

## CI (plan §9)

`lint`, `test`, `robustness`, `interface`, `notebook`, `traceability` (PRs only),
`ai-boundary`, `spec-frozen`. Each runs `tools/ci_local.sh <job>`; jobs skip
gracefully while tests or the notebook do not exist yet. `ai-boundary` fails
only if a commit with an AI `Co-Authored-By` trailer touches `docs/spec/`.
