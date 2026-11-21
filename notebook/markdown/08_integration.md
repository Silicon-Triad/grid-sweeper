## 4. Integration

`plan_and_execute` runs the CSP solver, sorts the tasks by slot to get the cleaning order,
then calls `execute_schedule`'s procedure (spec §7.2): start at the charger, `search` from the
current position to each next dirty cell, append each path without repeating the shared
endpoint, mark the cell cleaned, and finally `search` back to the charger.

- If the CSP finds no schedule, no search is run and failure is reported.
- If any leg has no path, the run stops and reports failure; it never claims success. The
  path walked so far and its cost are kept so the output shows where the robot got stuck
  (DEC-15).

Output (spec §7.2): schedule, visit sequence, each leg's path with cost and nodes expanded,
final grid (`C` charger, `##` obstacle, `Dk` dirty, `dk` cleaned, `*` path), total moves and
cost, and final status. It is shown below for both algorithms on our files.
