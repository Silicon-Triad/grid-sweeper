## 3. CSP scheduling

- **Variables:** every dirty cell `D1…Dn` (including those no constraint mentions).
- **Domains:** slots `{1…num_slots}`, ascending.
- **Constraints:** precedence `(A,B)` ⇒ slot(A) < slot(B); latest-slot `(A,Tk)` ⇒ slot(A) ≤ k;
  slot exclusivity (implicit) ⇒ no two tasks share a slot.

**Solver** (spec §6.5): backtracking with
- **MRV**, ties broken by the **degree heuristic** — number of distinct other unassigned
  tasks linked by precedence (DEC-05; exclusivity links every pair so it is not counted),
  then file order;
- **LCV** value ordering (fewest values ruled out for the other tasks first);
- **forward checking** after every assignment; a branch is rejected as soon as a domain is
  empty. Forward checking works on a copy of the domains, so backtracking restores the
  removed values automatically.

Values above a task's latest slot are removed before the search starts.

Below the schedule, every constraint is re-checked independently of the solver and printed
with ✓ / ✗ and the slots involved (spec §6.4).
