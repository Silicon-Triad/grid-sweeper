# UCS vs A* — comparative analysis (REQ-CMP-01, REQ-CMP-02, issue #16)

Data: `report/figures/search_comparison.md` (tables) and
`report/figures/search_comparison.png` (plots), regenerated with
`python tools/compare_search.py`. Timings are machine-dependent; costs and
node counts are deterministic (FIFO tie-break, REQ-SRCH-02).

## Quantitative

- **Path cost:** identical for UCS and A* in every run (5 charger→dirty pairs on
  `data/Environment.txt`, 10 scaling runs). Expected: Manhattan distance is
  admissible and consistent (DEC-02), so A* is optimal like UCS.
- **Nodes expanded, own environment:** A* expanded 23/16/59/31/19 nodes vs UCS
  41/35/72/62/54, i.e. 18–65 % fewer. The smallest gain (C→D3, 59 vs 72) is the
  goal in the far corner: the obstacle walls force detours, so many cells
  share the minimal f-value.
- **Scaling, corner→corner on open n×n grids:** both expand n²−1 nodes
  (24, 99, 399, 1599, 6399). Every cell in the start/goal bounding box has
  f = g + h = 2(n−1), so the heuristic cannot prune anything and A* ties UCS.
- **Scaling, midline (left-edge midpoint → right-edge midpoint):** A* expands
  exactly n−1 nodes (linear), UCS ≈ 0.75 n² (quadratic): 79 vs 4799 at 80×80.

## Qualitative

- UCS grows a "diamond" of equal g-cost around the start, blind to the goal's
  direction. A* elongates that diamond toward the goal; how much depends on how
  many cells tie on f.
- The heuristic's benefit depends on geometry: big when the optimal path is
  nearly unique (midline), zero when many equal-cost paths exist (open corner),
  and moderate with obstacles that make Manhattan distance underestimate.
- Per-node work is slightly higher for A* (one heuristic call per push), visible
  where both expand the same nodes (corner runs at small n); A* wins on time
  whenever it expands fewer nodes.
- Memory follows nodes expanded/frontier size, so the same comparison applies.
