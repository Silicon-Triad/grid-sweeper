### Test run 3b: infeasible schedule (`Environment.txt` + inline cyclic schedule)

The environment is our own (every cell reachable); the schedule is valid input but demands
`D1` before `D2` **and** `D2` before `D1`. No assignment can satisfy both, so the CSP solver
returns no schedule and the integration must report the failure without running any search:
the robot stays at the charging station (spec §7.1 item 6). The schedule is given inline, so
no extra input file is needed (spec §10.1).
