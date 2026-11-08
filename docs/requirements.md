# Requirements

Source of truth: `docs/spec/` (the PDFs win any conflict). Drafted by AI under issue #2 (docs/ is AI-permitted);
approved by all four team members. Status: **DRAFT — awaiting team approval**.

## ID scheme

`REQ-<AREA>-<NN>` — two-digit, never reused or renumbered.

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

Each requirement has: one parent spec §, rationale, and a verification method:
`test:<name>`, `notebook:<section>`, or `report:<section>`.

## Requirements

| ID | Requirement | Spec § | Rubric | Rationale | Verification |
|---|---|---|---|---|---|
| REQ-ENV-01 | Load the environment from `Environment.txt`; never hardcode it | §2, §5.2, §8.1 | C1 | Hidden files used at assessment | `test:test_env_parse_sample` |
| REQ-ENV-02 | Parse the 6-line format: `rows,cols`; obstacle count; obstacle tuples; dirty count; dirty tuples; charger tuple | §5.2 | C1 | Exact format is mandated | `test:test_env_parse_sample` |
| REQ-ENV-03 | Coordinates are zero-based `(row,col)`; top-left is `(0,0)` | §3, §5.2 | C1 | Defines state space | `test:test_env_coordinates` |
| REQ-ENV-04 | Label dirty cells D1…Dn in file order | §3, §5.2, §6.2 | C1 | Links env to CSP variables | `test:test_env_labels` |
| REQ-ENV-05 | Support any grid size and any number of obstacles/dirty cells | §2 | C1 | Hidden files may differ | `test:test_properties` |
| REQ-ENV-06 | Grid identifies free cells, obstacles, dirty cells and the charging station | §5.3 | C1 | Problem formulation | `test:test_env_grid_cells` |
| REQ-ENV-07 | State is the robot position `(row,col)`; initial state is the start passed to `search` | §5.3 | C1 | Problem formulation | `report:Problem Definition` |
| REQ-ENV-08 | Own `Environment.txt`: ≥8×8, ≥6 obstacles, ≥4 distinct dirty cells, exactly one charger, differs from sample | §4 | C1 | Minimum environment | `test:test_env_own_minimums` |
| REQ-ENV-09 | Own environment: every dirty cell reachable from the charger; no overlap among charger, dirty cells, obstacles | §4 | C1 | Environment must be solvable | `test:test_env_own_reachable` |
| REQ-SRCH-01 | Implement ≥1 uninformed (UCS) and ≥1 informed (A*) graph-search algorithm | §5.1 | C1 | Mandated algorithms | `test:test_search_algorithms` |
| REQ-SRCH-02 | Actions UP, DOWN, LEFT, RIGHT only; no diagonals | §2, §5.3 | C1 | Movement model | `test:test_successors_actions` |
| REQ-SRCH-03 | `get_successors(state, grid)` returns `(next_state, action, step_cost)`, excluding out-of-bounds and obstacle cells | §5.5 | C1 | Required function | `test:test_successors_bounds_obstacles` |
| REQ-SRCH-04 | Each valid move costs 1 | §5.3 | C1 | Step cost | `test:test_successors_cost` |
| REQ-SRCH-05 | `goal_test(state, goal_state)` returns True iff equal | §5.5 | C1 | Required function | `test:test_goal_test` |
| REQ-SRCH-06 | `path_cost(path)` = len(path) − 1; handles empty and single-state paths | §5.5 | C1 | Required function + named edge cases | `test:test_path_cost_edges` |
| REQ-SRCH-07 | `heuristic(state, goal_state)` estimates cost to goal (Manhattan) | §5.5 | C1 | Required function | `test:test_heuristic_manhattan` |
| REQ-SRCH-08 | Justify the heuristic's suitability (admissible, consistent) | §5.5 | C1 | Explicitly required | `report:Graph-Based Search Algorithms` |
| REQ-SRCH-09 | `search(grid, start, goal, algorithm)` returns path or no-path indication, cost, nodes_expanded | §5.5 | C1 | Required function | `test:test_search_returns` |
| REQ-SRCH-10 | Start and goal are inputs, not hardcoded in the algorithm | §5.4 | C1 | Reuse for integration | `test:test_search_arbitrary_pairs` |
| REQ-SRCH-11 | Same environment and start/goal pair solvable by each algorithm | §5.1, §5.4 | C1 | Fair comparison | `test:test_search_same_problem` |
| REQ-SRCH-12 | Every returned path has adjacent, in-bounds, obstacle-free steps | §5.4 | C1 | Validity | `test:test_properties` |
| REQ-SRCH-13 | Handle start == goal | §5.4 | C1 | Named edge case | `test:test_search_start_equals_goal` |
| REQ-SRCH-14 | Handle no path existing | §5.4 | C1 | Named edge case | `test:test_search_no_path` |
| REQ-CMP-01 | Report path, path cost and nodes expanded for each algorithm | §2, §5.4 | C4 | Required output | `notebook:Search Comparison` |
| REQ-CMP-02 | Compare algorithms on cost, nodes expanded, behaviour and performance; tables and/or graphs | §5.4, §8.2 | C4 | Rubric: quantitative + qualitative | `report:Results and Comparative Analysis` |
| REQ-CSP-01 | Load slots and constraints from `Schedule.txt`; never hardcode | §6.3 | C2 | Hidden files used at assessment | `test:test_schedule_parse_sample` |
| REQ-CSP-02 | Parse format: slot count; precedence count; `(before,after)` lines; latest-slot count; `(task,slot)` lines | §6.3 | C2 | Exact format is mandated | `test:test_schedule_parse_sample` |
| REQ-CSP-03 | Variables = all dirty cells from `Environment.txt`, including unconstrained tasks | §6.2, §6.4 | C2 | Explicitly required | `test:test_csp_unconstrained_tasks` |
| REQ-CSP-04 | Domains start as {T1…Tn} | §6.2 | C2 | Formulation | `test:test_csp_initial_domains` |
| REQ-CSP-05 | Precedence: before's slot strictly precedes after's slot | §6.2 | C2 | Constraint definition | `test:test_is_consistent_precedence` |
| REQ-CSP-06 | Latest-slot: task's slot ≤ given slot | §6.2 | C2 | Constraint definition | `test:test_is_consistent_latest` |
| REQ-CSP-07 | Slot exclusivity: at most one task per slot (implicit, not in file) | §6.2, §6.3 | C2 | Constraint definition | `test:test_is_consistent_exclusive` |
| REQ-CSP-08 | Validate: slots ≥ tasks; constraint labels match dirty cells | §6.4 | C2 | Input validity | `test:test_schedule_validation` |
| REQ-CSP-09 | Support any valid number of tasks, slots and constraints | §6.4 | C2 | Hidden files may differ | `test:test_properties` |
| REQ-CSP-10 | Own `Schedule.txt`: ≥3 precedence and ≥2 latest-slot constraints | §6.4 | C2 | Minimum constraints | `test:test_schedule_own_minimums` |
| REQ-CSP-11 | Every task gets exactly one slot; all constraints satisfied | §6.2, §6.4 | C2 | Validity | `test:test_csp_solution_valid` |
| REQ-CSP-12 | Report when no feasible schedule exists | §6.4 | C2 | Failure handling | `test:test_csp_infeasible` |
| REQ-CSP-13 | `select_unassigned_variable`: MRV, ties broken by degree (most constraints on unassigned vars) | §6.5 | C2 | Required function | `test:test_select_mrv_degree` |
| REQ-CSP-14 | `order_domain_values`: returns ordered candidate slots, using LCV | §6.5 | C2 | Required function (LCV optional in solver) | `test:test_order_lcv` |
| REQ-CSP-15 | `is_consistent`: checks every constraint evaluable with the current assignment | §6.5 | C2 | Required function | `test:test_is_consistent_partial` |
| REQ-CSP-16 | `forward_check`: prunes related unassigned domains; fails on any empty domain | §6.5 | C2 | Required function | `test:test_forward_check_prune_fail` |
| REQ-CSP-17 | Values removed by forward checking are restored on backtrack | §6.5 | C2 | Explicitly required | `test:test_forward_check_restore` |
| REQ-CSP-18 | `backtracking_search` uses select_unassigned_variable, is_consistent and forward_check; backtracks on failure | §6.5 | C2 | Required solver structure | `test:test_backtracking_solves_sample` |
| REQ-CSP-19 | Display the schedule and show each constraint is satisfied | §6.4 | C2 | Required output | `notebook:CSP Scheduling` |
| REQ-CSP-20 | Explain variables, domains, constraints and the role of each function | §6.4, §8.2 | C2 | Required explanation | `report:CSP Formulation and Implementation` |
| REQ-INT-01 | Order dirty cells by assigned slot to get the cleaning sequence | §7.1 | C3 | Integration step 2 | `test:test_integrate_order` |
| REQ-INT-02 | Start at the charging station; `search` from current position to each next dirty cell | §7.1, §7.2 | C3 | Procedure | `test:test_integrate_starts_at_charger` |
| REQ-INT-03 | Mark each dirty cell cleaned when reached | §7.1, §7.2 | C3 | Procedure | `test:test_integrate_marks_cleaned` |
| REQ-INT-04 | Return to the charging station via `search` | §7.1, §7.2 | C3 | Procedure | `test:test_integrate_returns` |
| REQ-INT-05 | `execute_schedule(grid, charging_station, schedule, algorithm)` returns complete_path, total_cost, success | §7.2 | C3 | Required function | `test:test_integrate_returns_tuple` |
| REQ-INT-06 | Join legs without duplicating shared endpoints | §7.2 | C3 | Procedure step 4 | `test:test_integrate_no_duplicate_joints` |
| REQ-INT-07 | Report failure (never success) on infeasible schedule or missing path | §7.1, §7.2 | C3 | Failure handling | `test:test_integrate_failure` |
| REQ-INT-08 | Display schedule, visit sequence, per-leg paths, final grid, total moves and cost, final status | §7.2 | C3 | Output requirements | `notebook:Integration` |
| REQ-INT-09 | Use real CSP and search outputs; components stay independently testable | §7.2 | C3 | No hardcoded decisions | `test:test_integrate_uses_components` |
| REQ-NB-01 | Single Jupyter notebook named `CS24045.ipynb` | §8.1 | all | Naming convention | `test:notebook (CI)` |
| REQ-NB-02 | First cell: Markdown with all members' names and roll numbers | §8.1 | all | Required | `notebook:Header` |
| REQ-NB-03 | Sections: environment loading, search, CSP, integration | §8.1 | all | Required structure | `notebook:structure` |
| REQ-NB-04 | Comments and Markdown explain implementation, algorithms, design decisions, results | §8.1 | all | Required | `notebook:review` |
| REQ-NB-05 | Notebook runs top-to-bottom using the submitted input files | §8.1 | all | Required | `test:notebook (CI)` |
| REQ-TEST-01 | Test run 1: own `Environment.txt` + `Schedule.txt` | §8.2 | C5 | Required test run | `report:Testing and Validation` |
| REQ-TEST-02 | Test run 2: `Environment_Sample.txt` + `Schedule_Sample.txt` | §8.2 | C5 | Required test run | `report:Testing and Validation` |
| REQ-TEST-03 | Test run 3: failure case via `Environment_Error.txt` / `Schedule_Error.txt` | §8.2 | C5 | Required test run | `report:Testing and Validation` |
| REQ-TEST-04 | Screenshots of configuration and output for all three runs, in notebook and report; failure screenshot shows detection and reporting | §8.2 | C5 | Required evidence | `report:Testing and Validation` |
| REQ-RPT-01 | Section: Problem Definition and Representation | §8.2 | C5 | Required section | `report:Problem Definition` |
| REQ-RPT-02 | Section: Graph-Based Search Algorithms (principles, pseudocode, heuristic) | §8.2 | C5 | Required section | `report:Graph-Based Search Algorithms` |
| REQ-RPT-03 | Section: CSP Formulation and Implementation | §8.2 | C5 | Required section | `report:CSP Formulation and Implementation` |
| REQ-RPT-04 | Section: System Integration | §8.2 | C5 | Required section | `report:System Integration` |
| REQ-RPT-05 | Section: Results and Comparative Analysis | §8.2 | C5 | Required section | `report:Results and Comparative Analysis` |
| REQ-RPT-06 | Section: Testing and Validation | §8.2 | C5 | Required section | `report:Testing and Validation` |
| REQ-RPT-07 | Section: Discussion and Improvements (completeness, optimality, limitations) | §8.2 | C5 | Required section | `report:Discussion` |
| REQ-RPT-08 | Section: References | §8.2 | C5 | Required section | `report:References` |
| REQ-RPT-09 | Generative AI declaration: whether used, purpose, team responsibility | §8.2 | C5 | Required | `report:GenAI Declaration` |
| REQ-RPT-10 | Rubric with names and roll numbers as title page; no other title page | §8.2 | C5 | Format | `report:Title page` |
| REQ-RPT-11 | Times New Roman, 11 pt body, 12 or 14 pt headings | §8.2 | C5 | Format | `report:format review` |
| REQ-RPT-12 | Online: `CS24045.ipynb`, `CS24045.pdf`, `Environment.txt`, `Schedule.txt`, `Environment_Error.txt`, `Schedule_Error.txt` on Classroom by 22 Nov | §8.2, §10.1 | C5 | Submission | `report:checklist (#31)` |
| REQ-RPT-13 | Hardcopy: double-sided, stapled, no plastic file | §8.2, §10.2 | C5 | Submission | `report:checklist (#31)` |

## Notes

- Test names are planned; Ashar (#7) may rename them. Update this table in the same PR.
- `order_domain_values` is a required function; the spec calls LCV "optional" for the solver. We implement it (plan #18).
- Not requirements, but tracked in `docs/decisions.md`: tie-breaking order in UCS/A*, output wording, `Grid`/`Constraints` structure (#3).
