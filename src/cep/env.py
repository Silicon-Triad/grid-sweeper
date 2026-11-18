"""Environment and schedule loading, grid representation, validation. Owner: Qazi.

Spec §5.2 (Environment Input File):
    "Use the following format, with one item or group of items per line:
    1. Grid dimensions as rows,columns.
    2. Number of obstacles.
    3. Coordinates of all obstacles, represented as (row,column) tuples.
    4. Number of dirty locations.
    5. Coordinates of all dirty locations, represented as (row,column) tuples.
    6. Coordinate of the charging station, represented as a (row,column) tuple.
    Coordinates are zero-based. The first dirty location listed is D1, the
    second is D2, and so on."

Spec §6.3 (Scheduling Input File):
    "1. Number of available time slots.
    2. Number of precedence constraints.
    3. One pair (task_before,task_after) per line for each precedence constraint.
    4. Number of latest-slot constraints.
    5. One pair (task,latest_slot) per line for each latest-slot constraint.
    Slot exclusivity applies automatically to all tasks and does not need to be
    listed in the file."

Spec §6.4:
    "The number of available time slots must be at least the number of dirty
    locations." / "Task labels used in the scheduling constraints must
    correspond to the dirty locations defined by Environment.txt."

Internal types (issue #3, DEC-06; also documented in AGENTS.md). All are team
choices where the spec is silent, except ``State`` (spec §5.3):
    - ``State``: ``(row, col)`` tuple of ints, zero-based (REQ-ENV-03).
    - ``Label``: task label ``"D1"`` … ``"Dn"`` in file order (REQ-ENV-04).
    - ``Slot``: int ``1`` … ``n``, displayed as ``T<n>``; ints because string
      order breaks at ten slots (``"T10" < "T9"``).
    - ``ACTIONS``: ``UP, DOWN, LEFT, RIGHT`` with their row/column deltas.
    - ``ALGORITHMS``: ``"ucs"``, ``"astar"`` (DEC-01).
    - ``Grid``, ``Constraints``: frozen dataclasses below.
Parsers and validation are added by issues #4 and #5.
"""

from collections.abc import Mapping
from dataclasses import dataclass

State = tuple[int, int]
Label = str
Slot = int

# Order matters: get_successors yields moves in this order, which fixes how
# UCS/A* break ties between equal-priority nodes. Spec order (§2, §5.3), DEC-06.
ACTIONS: tuple[tuple[str, tuple[int, int]], ...] = (
    ("UP", (-1, 0)),
    ("DOWN", (1, 0)),
    ("LEFT", (0, -1)),
    ("RIGHT", (0, 1)),
)

# search() raises ValueError for any other name, so a typo is never mistaken
# for "no path exists" (DEC-06).
ALGORITHMS: tuple[str, ...] = ("ucs", "astar")


@dataclass(frozen=True)
class Grid:
    """Environment loaded from Environment.txt (spec §5.3, REQ-ENV-06).

    Frozen so that no component can alter the shared environment; integration
    keeps its own record of cleaned cells (REQ-INT-03). Dirty and charger cells
    are passable: only out-of-bounds and obstacle cells block a move.

    Attributes:
        rows: Number of rows (file line 1).
        cols: Number of columns (file line 1).
        obstacles: Obstacle cells (file line 3); a frozenset for O(1) lookup in
            get_successors.
        dirty: Task label -> cell, in file order D1…Dn (file line 5). Read-only
            mapping; the parser wraps it in ``types.MappingProxyType``.
        charger: Charging station cell (file line 6); start and end of the
            robot's journey.
    """

    rows: int
    cols: int
    obstacles: frozenset[State]
    dirty: Mapping[Label, State]
    charger: State


@dataclass(frozen=True)
class Constraints:
    """Scheduling problem loaded from Schedule.txt (spec §6.2-§6.3).

    Slot exclusivity is implicit and not stored (REQ-CSP-07).

    Attributes:
        variables: Every task label in file order, including tasks without
            constraints (REQ-CSP-03). Carried here because
            select_unassigned_variable receives no ``variables`` argument but
            needs this order for its final tie-break (DEC-05).
        num_slots: Number of available time slots (file line 1).
        precedence: ``(before, after)`` pairs: ``before`` must get a strictly
            earlier slot (REQ-CSP-05).
        latest: Task label -> latest allowed slot (REQ-CSP-06). Read-only
            mapping; the parser wraps it in ``types.MappingProxyType``.
    """

    variables: tuple[Label, ...]
    num_slots: int
    precedence: tuple[tuple[Label, Label], ...]
    latest: Mapping[Label, Slot]


def initial_domains(constraints: Constraints) -> dict[Label, list[Slot]]:
    """Build the initial CSP domains (spec §6.2, REQ-CSP-04).

    Lists in ascending order keep value iteration, and hence the schedule
    found, deterministic (DEC-06). Each variable gets its own list so that
    pruning one domain never affects another.

    Args:
        constraints: Scheduling problem; supplies variables and slot count.

    Returns:
        Mapping from every variable to ``[1, …, num_slots]``.
    """
    return {v: list(range(1, constraints.num_slots + 1)) for v in constraints.variables}
