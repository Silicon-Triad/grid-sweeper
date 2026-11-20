<!-- Notebook markdown cell for issue #15 (REQ-SRCH-08); tools/build_notebook.py (#27) places it after the search code. -->
### Why Manhattan distance is the right heuristic for A*

The spec (§5.5) lets us use Manhattan distance, `h(n) = |row_n − row_goal| + |col_n − col_goal|`,
and asks us to explain why the heuristic suits the environment and the algorithm (DEC-02).

**Admissible (never overestimates).** The robot moves only UP, DOWN, LEFT or RIGHT, and every
move costs 1 (§5.3). One move changes either the row or the column by exactly 1, so it can reduce
the Manhattan distance by at most 1. Reaching the goal therefore takes at least `h(n)` moves, and
obstacles can only make the real path longer, never shorter. So `h(n) ≤ h*(n)` for every cell.

**Consistent (monotone).** For any move from `n` to a neighbour `n'` with cost `c(n, n') = 1`,
the Manhattan distance changes by exactly ±1, so `h(n) ≤ c(n, n') + h(n')`. Also `h(goal) = 0`.
Consistency implies admissibility, and it means `f = g + h` never decreases along a path.

**Why this matters for A\*.** Our A\* is a graph search (it keeps an explored set). With a
consistent heuristic, the first time A\* expands a cell it has already found the cheapest path to
it, so it never has to reopen a cell and the path it returns is optimal — the same cost UCS finds.

**Why not something else.** Euclidean distance is also admissible but is never larger than
Manhattan on this grid, so it is less informed and A\* would expand more nodes. `h = 0` turns A\*
into UCS. A heuristic that ignores the four-direction rule (e.g. Chebyshev, for diagonal moves)
would be weaker still. Manhattan is the largest of these that is still admissible, so it gives
the fewest expansions without losing optimality.
