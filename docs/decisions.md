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

### DEC-04 — `path_cost` of an empty path — **OPEN**
- **Issue:** #39
- **Spec reference:** §5.5 "An empty path … must be handled appropriately"
- **Question:** What value (or error) does `path_cost([])` return?
- **Options considered:** 0; `None`/`inf`; raise `ValueError`
- **Decision:** *pending — Mujtaba*
- **Rationale:**
- **Affects REQ-IDs:** REQ-SRCH-06
- **Decided by / date:**

### DEC-05 — Degree heuristic: what counts as a connection — **OPEN**
- **Issue:** #40
- **Spec reference:** §6.5 "the variable connected to the largest number of other unassigned variables through constraints"
- **Question:** Count distinct variables or constraints? Does slot exclusivity count (if so, every variable ties)?
- **Options considered:** precedence only; precedence + exclusivity
- **Decision:** *pending — Huzaifa*
- **Rationale:**
- **Affects REQ-IDs:** REQ-CSP-13
- **Decided by / date:**
