# Design decisions

Decisions taken where the spec (`docs/spec/`) is silent or ambiguous. Each one
comes from a `spec-question` issue, is labelled `design-decision`, and is
**never presented as a spec value**.

## Template

### DEC-NN — <short title>
- **Issue:** #
- **Spec reference:** § (quote the silent/ambiguous text)
- **Question:**
- **Options considered:**
- **Decision:**
- **Rationale:**
- **Affects REQ-IDs:**
- **Decided by / date:**

<!-- Add decisions below this line, newest last. -->

### DEC-01 — Search algorithms: UCS (uninformed) and A* (informed)
- **Issue:** #38
- **Spec reference:** §5.1 "at least one uninformed and one informed search algorithm"
- **Question:** Which algorithms?
- **Options considered:** BFS or UCS (uninformed); greedy best-first or A* (informed)
- **Decision:** UCS and A*
- **Rationale:** With unit step cost both are optimal, so the comparison isolates the effect of the heuristic; UCS and A* share one priority-queue implementation.
- **Affects REQ-IDs:** REQ-SRCH-01, REQ-CMP-01, REQ-CMP-02
- **Decided by / date:** Qazi (planning), 2026-11-02; team confirms via PR #36

### DEC-02 — Heuristic: Manhattan distance
- **Issue:** #38
- **Spec reference:** §5.5 "students **may** use Manhattan distance"
- **Question:** Which heuristic?
- **Options considered:** Manhattan; Euclidean; zero
- **Decision:** Manhattan distance
- **Rationale:** With four-directional unit-cost moves it never overestimates (admissible) and satisfies the triangle inequality per move (consistent), and it dominates Euclidean.
- **Affects REQ-IDs:** REQ-SRCH-07, REQ-SRCH-08
- **Decided by / date:** Qazi (planning), 2026-11-02; team confirms via PR #36

### DEC-03 — Notebook and report filename: CS24045
- **Issue:** #38
- **Spec reference:** §8.1, §8.2 "CS24XXX … roll number of any one group member"
- **Question:** Whose roll number?
- **Options considered:** any of CS-24035, CS-24039, CS-24045, CS-24047
- **Decision:** CS24045 (Qazi)
- **Rationale:** Qazi owns notebook consolidation and submission (#27, #31).
- **Affects REQ-IDs:** REQ-NB-01, REQ-RPT-12
- **Decided by / date:** Qazi (planning), 2026-11-02; team confirms via PR #36

### DEC-04 — `path_cost` of an empty path — **DECIDED**
- **Issue:** #39
- **Spec reference:** §5.5 "An empty path … must be handled appropriately"
- **Question:** What value (or error) does `path_cost([])` return?
- **Options considered:** 0; `None`/`inf`; raise `ValueError`
- **Decision:** `path_cost([])` returns `0` (team choice, not a spec value). Single-state path → `0` per the spec formula.
- **Rationale:** An empty path contains no moves, so 0 is consistent with "cost = number of movements" and keeps the `int` return type. "No path" is signalled by `search` returning `(None, None, nodes_expanded)` (§5.5), never by `path_cost`; `execute_schedule` must check `success`/`None`, not rely on cost, to detect an unreachable leg. In normal runs `[]` never reaches `path_cost` — only direct calls (tests).
- **Affects REQ-IDs:** REQ-SRCH-06
- **Decided by / date:** Qazi, 2026-11-18

### DEC-05 — Degree heuristic: what counts as a connection — **DECIDED**
- **Issue:** #40
- **Spec reference:** §6.5 "the variable connected to the largest number of other unassigned variables through constraints"
- **Question:** Count distinct variables or constraints? Does slot exclusivity count (if so, every variable ties)?
- **Options considered:** precedence only; precedence + exclusivity
- **Decision:** Degree = number of *distinct other unassigned variables* linked to the variable by a precedence constraint. Slot exclusivity is not counted. Ties remaining after MRV + degree are broken by file order (D1…Dn) (team choice, not a spec value).
- **Rationale:** Follows the spec wording ("number of other unassigned variables"). Exclusivity links every pair of unassigned variables, adding the same constant to every score, so it never changes the ranking; excluding it keeps the count meaningful. The file-order tie-break makes variable order — and hence the schedule found when several are valid — deterministic and testable. Affects only which valid schedule is found and search effort, never feasibility.
- **Affects REQ-IDs:** REQ-CSP-13
- **Decided by / date:** Qazi, 2026-11-18

### DEC-06 — Internal types: `Grid`, `Constraints`, slots, schedule — **DECIDED**
- **Issue:** #3
- **Spec reference:** §5.5 "grid: Environment representation"; §6.5 "constraints: Scheduling constraints"; §7.2 "schedule: Cleaning tasks ordered according to their assigned time slots" — structure not specified.
- **Question:** How are `Grid`, `Constraints`, slots and the `schedule` argument represented?
- **Options considered:** (A) plain dicts/sets; (B) frozen dataclasses; (C) cell-character matrix + metadata. Slots as ints vs `"T<n>"` strings. Schedule as labels vs `(label, state)` pairs. Variable order inside `Constraints` vs derived from label numbers.
- **Decision:** (B) frozen dataclasses `Grid(rows, cols, obstacles, dirty, charger)` and `Constraints(variables, num_slots, precedence, latest)`; slots are ints `1…n` (displayed `T<n>`); `schedule` is a list of labels in slot order, converted to cells via `grid.dirty`; `variables` (file order) lives in `Constraints`. Domains are `dict[label, list[int]]` in ascending order, built by `env.initial_domains`. Actions are plain strings in the order UP, DOWN, LEFT, RIGHT (the spec's listing order, §2/§5.3), which fixes successor order and hence UCS/A* tie-breaks. `search` raises `ValueError` for an algorithm name other than `"ucs"`/`"astar"`. `Grid.dirty` and `Constraints.latest` are read-only mappings (`MappingProxyType`). Full table in AGENTS.md "Internal types". Team choices, not spec values.
- **Rationale:** Typos in field names fail at once; immutability stops integration marking cells cleaned on the shared grid (REQ-INT-03 runs repeat per algorithm). Int slots avoid string-order bugs at ≥10 slots/tasks (`"T10" < "T9"`). `select_unassigned_variable` receives no `variables` argument yet needs file order for DEC-05, so `Constraints` carries it. Labels as the schedule match the spec wording "cleaning tasks". Ordered lists and a fixed action order make the schedule and paths found reproducible (testable); raising on an unknown algorithm keeps a typo distinct from "no path" (REQ-INT-07).
- **Affects REQ-IDs:** REQ-ENV-03, REQ-ENV-06, REQ-ENV-07, REQ-CSP-04, REQ-CSP-13, REQ-SRCH-02, REQ-SRCH-09, REQ-INT-01
- **Decided by / date:** Qazi, 2026-11-18

### DEC-07 — Input errors: one `InputError(ValueError)` class, first error wins — **DECIDED**
- **Issue:** #4, #5
- **Spec reference:** §5.2, §6.3, §6.4 — no error mechanism or message format given.
- **Question:** Which exception type(s) and message style do the parsers use?
- **Options considered:** one `InputError(ValueError)`; separate env/schedule classes; plain `ValueError`
- **Decision:** One class `InputError(ValueError)` in `src/cep/env.py`, raised at the first problem found. Message: `"<source>: line <n>: <problem>"`, naming the offending value (team choice, not a spec value).
- **Rationale:** Tests (#7) and the error run (#26) can match one type and the line number; subclassing `ValueError` keeps generic handlers working.
- **Affects REQ-IDs:** REQ-ENV-06, REQ-CSP-08
- **Decided by / date:** Qazi, 2026-11-18

### DEC-08 — Whitespace tolerance — **DECIDED**
- **Issue:** #4, #5
- **Spec reference:** §5.2 / §6.3 give the format by example only (`Environment_Sample.txt`, `Schedule_Sample.txt`).
- **Question:** Are spaces inside tuples, Windows line endings and trailing blank lines accepted?
- **Options considered:** strict sample format; tolerant
- **Decision:** Tolerant: spaces around numbers, commas and parentheses (`( 2 , 3 )`), `\r\n` line endings and trailing blank lines are accepted. Blank lines between items are errors, except the empty tuple line of DEC-09 (team choice, not a spec value).
- **Rationale:** Hidden assessment files may be hand-typed on any OS; whitespace carries no meaning in the format.
- **Affects REQ-IDs:** REQ-ENV-02, REQ-CSP-02
- **Decided by / date:** Qazi, 2026-11-18
- **Revised 2026-11-22 (#70):** Blank and whitespace-only lines are ignored anywhere in both files (before, between and after items). Reason: notebook review — no item of either format is ever an empty line (counts, tuple lines with count > 0, pairs), so dropping blank lines cannot change the meaning of any file that was accepted before; it only accepts hand-typed files with spacing between sections. Consistent with DEC-09: the optional empty tuple line after a count of 0 is now simply one of the dropped blank lines, so both layouts still parse identically. Line numbers in error messages stay the original ones.

### DEC-09 — Tuple line when a count is 0 — **DECIDED**
- **Issue:** #4, #5
- **Spec reference:** §5.2 lines 3 and 5; §6.3 items 3 and 5 — the zero case is not shown.
- **Question:** After a count of 0, is the tuple line empty, missing, or either?
- **Options considered:** empty line required; line omitted; both accepted
- **Decision:** Environment: both accepted — after a count of 0, an empty line is consumed as the empty list, otherwise the next line is read as the next item (unambiguous: count lines are never empty). Schedule: a count of 0 means no pair lines follow (team choice, not a spec value).
- **Rationale:** Either reading of the spec is plausible; accepting both costs one check.
- **Affects REQ-IDs:** REQ-ENV-02, REQ-CSP-02
- **Decided by / date:** Qazi, 2026-11-18

### DEC-10 — Tuples per line — **DECIDED**
- **Issue:** #4, #5
- **Spec reference:** §5.2 "one item or group of items per line" (sample: all obstacles on one line, `", "`-separated); §6.3 "One pair … per line".
- **Question:** One line per group, or one tuple per line?
- **Options considered:** strict per file type; accept both layouts
- **Decision:** Environment: each tuple group on one line, tuples separated by commas and/or spaces. Schedule: exactly one pair per line (follows the spec wording; layout strictness is a team choice).
- **Rationale:** Matches the samples; keeps line numbers in errors meaningful and the parser simple to explain.
- **Affects REQ-IDs:** REQ-ENV-02, REQ-CSP-02
- **Decided by / date:** Qazi, 2026-11-18

### DEC-11 — Environment value checks — **DECIDED**
- **Issue:** #4
- **Spec reference:** §4 ("distinct dirty locations", "No overlap"); §5.2 — limits on values not given.
- **Question:** How are duplicates, non-positive sizes, negative counts, count mismatches, overlaps, extra lines, zero dirty cells and reachability handled?
- **Options considered:** reject vs. silently fix / pass on
- **Decision:** Errors: duplicate cell within obstacles or within dirty cells; rows or cols ≤ 0; negative count; non-integer value (malformed); count ≠ number of tuples (message gives both); cell out of bounds or negative; any overlap among charger, dirty cells and obstacles (message names both roles); non-blank lines after line 6. Allowed: 0 obstacles, 0 dirty cells. Not checked by the parser: reachability — it is a property of our own file (REQ-ENV-09, a test) and a failure `execute_schedule` reports (§7.1 item 6) (team choice, not a spec value).
- **Rationale:** Duplicate dirty cells would give two labels one cell; duplicate obstacles are harmless but almost certainly typos. Leaving reachability to search keeps "unreachable" a demonstrable runtime failure.
- **Affects REQ-IDs:** REQ-ENV-02, REQ-ENV-06
- **Decided by / date:** Qazi, 2026-11-18
- **Revised 2026-11-22 (#70):** Overlap stays an error (dirty cell on the charger included) — it is a spec rule, not a team choice: §4 "The charging station, dirty locations, and obstacles must occupy different cells." The error message now cites §4. Blank lines after line 6 are ignored (DEC-08 revised); non-blank extra lines remain errors.

### DEC-12 — Schedule value checks — **DECIDED**
- **Issue:** #5
- **Spec reference:** §6.3, §6.4 — duplicates, slot ranges, self-precedence and slot spelling not covered.
- **Question:** How are duplicate constraints, out-of-range latest slots, `(X,X)`, slot spelling, label case and extra lines handled?
- **Options considered:** reject vs. pass to the CSP solver; `T3` and/or `3`
- **Decision:** Exact duplicate precedence pair: allowed (kept once). Two latest-slot entries for one task: error. Latest slot < 1 or > num_slots: error. `(X,X)` and precedence cycles: accepted — the solver reports no feasible schedule (REQ-CSP-12). Slots accepted as `T3` (sample) or `3`, stored as int. Labels case-sensitive `D<n>`; a label not in the grid is an error naming it (REQ-CSP-08). Non-blank lines after the last pair: error (team choice, not a spec value).
- **Rationale:** Malformed references are input errors; well-formed but unsatisfiable constraints are infeasibility, which the error run must show the solver detecting.
- **Affects REQ-IDs:** REQ-CSP-02, REQ-CSP-08, REQ-CSP-12
- **Decided by / date:** Qazi, 2026-11-18
- **Revised 2026-11-22 (#70):** Two or more latest-slot entries for one task are accepted; the smallest (tightest) slot is kept. Reason: notebook review — both limits must hold, and `slot ≤ a` and `slot ≤ b` is exactly `slot ≤ min(a, b)`, so nothing is lost. Each entry is still checked: unknown label or slot outside T1..Tn is an error.

### DEC-13 — Text parsers alongside file loaders — **DECIDED**
- **Issue:** #4, #5
- **Spec reference:** §5.2, §6.3 require loading from files; function names not given.
- **Question:** Parse only from files, or also from text?
- **Options considered:** `load_*` only; `load_*` + `parse_*`
- **Decision:** `parse_environment(text, source)` / `parse_schedule(text, grid, source)` do the work; `load_environment(path)` / `load_schedule(path, grid)` read the file and pass its name as `source` for error messages (team choice).
- **Rationale:** Tests can use inline strings; file reading stays one line.
- **Affects REQ-IDs:** REQ-ENV-01, REQ-CSP-01
- **Decided by / date:** Qazi, 2026-11-18

### DEC-14 — What counts as a node expanded in `search` — **DECIDED**
- **Issue:** #51
- **Spec reference:** §5.5 "nodes_expanded: Number of nodes expanded during the search" — when a node counts is not stated.
- **Question:** Does the goal count? What does start == goal report?
- **Options considered:** (A) count a node when its successors are generated; goal tested on pop and not counted; (B) count every node popped, including the goal; (C) count nodes generated
- **Decision:** (A), as implemented in PR #50: start == goal → `([start], 0, 0)`; no path → number of reachable cells expanded (team choice, not a spec value).
- **Rationale:** Matches the textbook meaning of "expand" (generate successors); the goal's successors are never generated. A and B rank UCS vs A* identically (B adds +1 to every successful search). C measures something else.
- **Affects REQ-IDs:** REQ-SRCH-09, REQ-SRCH-13, REQ-CMP-01, REQ-CMP-02
- **Decided by / date:** Qazi, 2026-11-21

### DEC-15 — `execute_schedule` return values on failure — **DECIDED**
- **Issue:** #23
- **Spec reference:** §7.2 step 9 "report failure rather than claim that the cleaning task was completed successfully" — the content of `complete_path`/`total_cost` on failure is not stated.
- **Question:** On a leg with no path, what are `complete_path` and `total_cost`?
- **Options considered:** partial path walked so far + its cost; `(None, None, False)`
- **Decision:** Stop at the first leg with no path and return the path walked so far (from the charger to the last cell reached), its cost, and `success=False`. If the CSP finds no schedule, no search is run: path `[charger]`, cost 0, failure (team choice, not a spec value).
- **Rationale:** Shows where the robot got stuck; the display (#24) prints the failure reason. `success` alone decides success (DEC-04).
- **Affects REQ-IDs:** REQ-INT-05, REQ-INT-07
- **Decided by / date:** Qazi, 2026-11-21
