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
Environment parsing: issue #4 (rules DEC-07 to DEC-11, DEC-13). Schedule parsing: #5.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

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


class InputError(ValueError):
    """Invalid Environment.txt or Schedule.txt content (DEC-07).

    One class for both files so callers and tests catch a single type. The
    message always starts with ``"<source>: line <n>:"``.
    """


# One "(row,col)" tuple. "-?" lets a negative number parse so the error can
# say "outside the grid" rather than the vaguer "malformed" (DEC-11).
_CELL_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def _numbered_lines(text: str) -> list[tuple[int, str]]:
    """Split text into ``(line_number, stripped_line)`` pairs.

    Trailing blank lines are dropped; ``splitlines`` also handles ``\\r\\n``
    (DEC-08).

    Args:
        text: Whole file content.

    Returns:
        1-based line numbers paired with whitespace-stripped lines.
    """
    lines = [(i, line.strip()) for i, line in enumerate(text.splitlines(), start=1)]
    while lines and not lines[-1][1]:
        lines.pop()
    return lines


class _LineReader:
    """Hands out lines one at a time and builds located error messages."""

    def __init__(self, text: str, source: str) -> None:
        """Prepare to read ``text``.

        Args:
            text: Whole file content.
            source: Name used in error messages (usually the file name).
        """
        self.lines = _numbered_lines(text)
        self.pos = 0
        self.source = source

    def error(self, lineno: int, problem: str) -> InputError:
        """Build an InputError in the DEC-07 format.

        Args:
            lineno: 1-based line number the problem is on.
            problem: What is wrong, naming the bad value.

        Returns:
            The exception (the caller raises it).
        """
        return InputError(f"{self.source}: line {lineno}: {problem}")

    def next(self, what: str) -> tuple[int, str]:
        """Return the next line; blank lines between items are errors (DEC-08).

        Args:
            what: Description of the expected item, for the error message.

        Returns:
            ``(line_number, stripped_line)``.

        Raises:
            InputError: If the file ended or the line is blank.
        """
        if self.pos >= len(self.lines):
            last = self.lines[-1][0] if self.lines else 0
            raise self.error(last + 1, f"missing {what} (file ended)")
        lineno, line = self.lines[self.pos]
        self.pos += 1
        if not line:
            raise self.error(lineno, f"expected {what}, found a blank line")
        return lineno, line

    def skip_empty_line(self) -> None:
        """Consume one blank line if it is next (empty tuple line, DEC-09)."""
        if self.pos < len(self.lines) and not self.lines[self.pos][1]:
            self.pos += 1

    def expect_end(self) -> None:
        """Raise if any line is left over (DEC-11, DEC-12).

        Raises:
            InputError: On the first unexpected line.
        """
        if self.pos < len(self.lines):
            lineno, line = self.lines[self.pos]
            raise self.error(lineno, f"unexpected extra line {line!r}")


def _parse_count(reader: _LineReader, what: str) -> int:
    """Read a line holding one non-negative integer.

    Args:
        reader: Line source.
        what: Name of the count, for error messages.

    Returns:
        The count.

    Raises:
        InputError: If the line is not a non-negative integer (DEC-11).
    """
    lineno, line = reader.next(what)
    if not re.fullmatch(r"\d+", line):
        raise reader.error(
            lineno, f"{what} must be a non-negative integer, got {line!r}"
        )
    return int(line)


def _parse_cells(line: str) -> list[State] | None:
    """Parse a line of ``(row,col)`` tuples separated by commas/spaces (DEC-10).

    Args:
        line: Stripped line, possibly empty.

    Returns:
        Cells in line order, or None if anything besides tuples, commas and
        spaces is on the line.
    """
    # Whatever is left after removing the tuples must only be separators.
    leftover = _CELL_RE.sub(" ", line)
    if leftover.replace(",", " ").strip():
        return None
    return [(int(r), int(c)) for r, c in _CELL_RE.findall(line)]


def parse_environment(text: str, source: str = "Environment.txt") -> Grid:
    """Parse Environment.txt content into a Grid (spec §5.2, REQ-ENV-02).

    Format, one item or group per line: ``rows,cols``; obstacle count;
    obstacle tuples; dirty count; dirty tuples; charger tuple. Validation rules
    are DEC-07 to DEC-11.

    Args:
        text: Whole file content.
        source: Name used in error messages.

    Returns:
        The validated Grid; dirty labels D1…Dn in file order (REQ-ENV-04).

    Raises:
        InputError: On the first format or validation problem found.
    """
    reader = _LineReader(text, source)

    lineno, line = reader.next("grid dimensions 'rows,cols'")
    match = re.fullmatch(r"(\d+)\s*,\s*(\d+)", line)
    if not match:
        raise reader.error(lineno, f"grid dimensions must be 'rows,cols', got {line!r}")
    rows, cols = int(match[1]), int(match[2])
    if rows <= 0 or cols <= 0:
        raise reader.error(
            lineno, f"grid dimensions must be positive, got {rows}x{cols}"
        )

    # cell -> (role, line it came from); used for the overlap check (§4).
    seen: dict[State, tuple[str, int]] = {}

    def read_cells(what: str, count: int) -> list[State]:
        """Read one tuple line of exactly ``count`` distinct in-bounds cells."""
        if count == 0:
            reader.skip_empty_line()  # DEC-09: empty line or none at all
            return []
        lineno, line = reader.next(f"{what} coordinates")
        cells = _parse_cells(line)
        if cells is None:
            raise reader.error(lineno, f"malformed {what} coordinates {line!r}")
        if len(cells) != count:
            raise reader.error(
                lineno, f"expected {count} {what} cells, found {len(cells)}"
            )
        for cell in cells:
            check_cell(cell, what, lineno)
        return cells

    def check_cell(cell: State, what: str, lineno: int) -> None:
        """Reject out-of-bounds, duplicate and overlapping cells (DEC-11)."""
        r, c = cell
        if not (0 <= r < rows and 0 <= c < cols):
            raise reader.error(lineno, f"{what} cell {cell} outside {rows}x{cols} grid")
        if cell in seen:
            other, other_line = seen[cell]
            if other == what:
                raise reader.error(lineno, f"duplicate {what} cell {cell}")
            raise reader.error(
                lineno, f"{what} cell {cell} overlaps {other} cell (line {other_line})"
            )
        seen[cell] = (what, lineno)

    obstacles = read_cells("obstacle", _parse_count(reader, "obstacle count"))
    dirty_cells = read_cells("dirty", _parse_count(reader, "dirty count"))

    lineno, line = reader.next("charging station coordinate")
    charger_cells = _parse_cells(line)
    if charger_cells is None or len(charger_cells) != 1:
        raise reader.error(
            lineno, f"charging station must be one (row,col) tuple, got {line!r}"
        )
    charger = charger_cells[0]
    check_cell(charger, "charging station", lineno)

    reader.expect_end()

    # D1…Dn in file order (REQ-ENV-04); dicts keep insertion order.
    dirty = {f"D{i}": cell for i, cell in enumerate(dirty_cells, start=1)}
    return Grid(
        rows=rows,
        cols=cols,
        obstacles=frozenset(obstacles),
        dirty=MappingProxyType(dirty),
        charger=charger,
    )


def load_environment(path: str | Path) -> Grid:
    """Load and validate an Environment.txt file (REQ-ENV-01).

    Args:
        path: File to read; supplied by the caller, never hardcoded.

    Returns:
        The validated Grid.

    Raises:
        InputError: If the content is invalid (message names the file).
        OSError: If the file cannot be read.
    """
    path = Path(path)
    return parse_environment(path.read_text(encoding="utf-8"), source=path.name)
