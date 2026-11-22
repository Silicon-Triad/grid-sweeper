### Backtracking demo

`Schedule.txt` and the sample schedule are solved without a dead end, so they never show
backtracking. The schedule below (given inline, on our own grid) is the smallest feasible one
we found by searching random schedules that makes the solver backtrack: a precedence chain
`D5 → D3 → D1 → D2` in 5 slots.

`backtracking_search_with_stats` is the same solver as the frozen `backtracking_search`
(which calls it and drops the counters, DEC-16). The counters mean:
- **assignments_tried** — values that passed the constraint check and were assigned;
- **fc_rejections** — of those, assignments forward checking rejected at once (a domain became empty);
- **backtracks** — assignments that passed forward checking but whose whole subtree failed,
  so they were undone;
- **values_pruned** — domain values removed by successful forward checks;
- **values_restored** — of those, the values given back when their branch was abandoned
  (spec §6.5: "Any domain values removed during forward checking must be restored when backtracking").

The sentence printed under the table reads the counters of this run. The schedule found is then
re-checked constraint by constraint.
