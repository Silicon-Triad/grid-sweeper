<!-- Report paragraph for "Graph-Based Search Algorithms" (issue #15, REQ-SRCH-08). -->
**Heuristic choice.** For A\* we use Manhattan distance, `h(n) = |row_n − row_goal| + |col_n − col_goal|`
(spec §5.5; DEC-02). It is admissible: each move is UP, DOWN, LEFT or RIGHT at cost 1, so one move
reduces the Manhattan distance by at most 1, and obstacles can only lengthen the real path; hence
`h(n)` never exceeds the true remaining cost. It is also consistent: for any move from `n` to a
neighbour `n'`, `h(n) ≤ 1 + h(n')`, and `h(goal) = 0`. Because our A\* is a graph search with an
explored set, consistency guarantees that each cell is expanded first along a cheapest path, so A\*
returns an optimal path with the same cost as UCS without reopening cells. Among admissible options
it is the most informed: Euclidean distance and `h = 0` are never larger, so they would make A\*
expand more nodes, and `h = 0` reduces A\* to UCS.
