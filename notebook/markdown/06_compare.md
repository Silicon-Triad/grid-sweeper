### UCS vs A\* on our environment

Each pair runs both algorithms from the charging station to each dirty cell. Path costs
must be equal (both are optimal); the difference is in nodes expanded. The scaling runs use
open n×n grids: corner-to-corner (A\* has nothing to prune, every cell in the box has the same
`f`) and edge-midpoint to edge-midpoint (A\*'s best case).
