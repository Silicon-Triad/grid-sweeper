## 1. Environment loading

`Environment.txt` (spec §5.2) is parsed into a frozen `Grid` dataclass: dimensions, a
`frozenset` of obstacle cells, the dirty cells labelled `D1…Dn` in file order, and the
charging station. `Schedule.txt` (spec §6.3) is parsed into a frozen `Constraints`
dataclass. Slots are stored as integers (shown as `T<n>`) so that `T10` sorts after `T9`.

**Design decisions** (team choices where the spec is silent, see `docs/decisions.md`):
- DEC-06: frozen dataclasses — no component can change the shared grid; integration keeps
  its own record of cleaned cells.
- DEC-07: every input problem raises one `InputError` whose message names the file, the
  line and the bad value; the first problem found is reported.
- DEC-08 – DEC-12: tolerant whitespace, one tuple group per line, duplicates/overlaps/out-of-bounds
  cells rejected, slots written `T3` or `3`.
  Reachability is *not* checked by the parser: an unreachable cell is a runtime failure the
  integration must detect and report (§7.1 item 6).

**Input tolerance** (DEC-08, DEC-11, DEC-12, revised for #70):
- *Accepted:* blank or whitespace-only lines anywhere (no item is ever an empty line, so this
  changes the meaning of no file; the optional empty line after a count of 0 is one of them);
  spaces inside tuples; Windows line endings; slots as `T3` or `3`; a repeated precedence pair
  (kept once); several latest-slot entries for one task (the smallest is kept — both must hold,
  so this is exact); `(X,X)` and precedence cycles (the solver reports them as infeasible).
- *Rejected* (`InputError`): wrong counts; malformed lines; cells outside the grid; duplicate
  cells; any overlap of charger, dirty cells and obstacles — including a dirty cell on the
  charger (spec §4: they "must occupy different cells"); unknown task labels; latest slots
  outside `T1…Tn`; fewer slots than tasks; extra non-blank lines.
