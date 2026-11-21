## 2. Graph-based search

- **State:** `(row, col)`; **actions:** UP, DOWN, LEFT, RIGHT (in that order, which fixes
  tie-breaking); a move is valid if it stays inside the grid and does not enter an obstacle;
  **step cost:** 1; **goal test:** `state == goal_state` (spec §5.3).
- **Algorithms (DEC-01):** Uniform-Cost Search (uninformed) and A\* (informed). Both use the
  same best-first graph search with a priority queue; UCS orders by `g(n)`, A\* by
  `g(n) + h(n)`. The goal is tested when a node is taken off the queue, which is what makes
  both optimal. A counter breaks equal priorities first-in-first-out, so results are
  deterministic.
- **Nodes expanded (DEC-14):** a node counts when its successors are generated; the goal node
  is not counted, so start == goal gives `([start], 0, 0)`.
- **No path:** `search` returns `(None, None, nodes_expanded)`; an unknown algorithm name
  raises `ValueError` so a typo is never mistaken for "no path".
- `path_cost([])` returns 0 (DEC-04).
