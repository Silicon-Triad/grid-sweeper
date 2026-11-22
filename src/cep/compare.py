"""UCS vs A* comparison (spec §5.4, §8.2; REQ-CMP-01, REQ-CMP-02). Owner: Mujtaba.

Spec §5.4: "Compare the implemented algorithms in terms of path cost, nodes
expanded, and their behavior and performance." Spec §8.2: "Present tabular
and/or graphical comparisons..."

Only the frozen ``search`` interface is used, so the comparison measures the
same code the notebook and integration run.
"""

import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from tabulate import tabulate

from cep.env import ALGORITHMS, Grid, State
from cep.search import search


@dataclass(frozen=True)
class Run:
    """One search run for the comparison table (REQ-CMP-01)."""

    label: str
    algorithm: str
    start: State
    goal: State
    path: list[State] | None
    cost: int | None
    nodes_expanded: int
    seconds: float


def run_pair(
    grid: Grid, start: State, goal: State, label: str = "", repeats: int = 1
) -> list[Run]:
    """Run every algorithm on one start/goal pair.

    Args:
        grid: Environment representation.
        start: Starting position.
        goal: Target position.
        label: Name shown in the table.
        repeats: Timing repetitions; the minimum is kept because it is the
            least affected by OS noise.

    Returns:
        One ``Run`` per algorithm, in ``ALGORITHMS`` order.
    """
    runs = []
    for algorithm in ALGORITHMS:
        best = float("inf")
        for _ in range(max(1, repeats)):
            t0 = time.perf_counter()
            path, cost, nodes = search(grid, start, goal, algorithm)
            best = min(best, time.perf_counter() - t0)
        runs.append(Run(label, algorithm, start, goal, path, cost, nodes, best))
    return runs


def compare_pairs(
    grid: Grid, pairs: Iterable[tuple[str, State, State]], repeats: int = 1
) -> list[Run]:
    """Compare all algorithms on several labelled start/goal pairs.

    Args:
        grid: Environment representation.
        pairs: ``(label, start, goal)`` triples.
        repeats: Timing repetitions per run.

    Returns:
        Runs for every pair and algorithm.
    """
    runs: list[Run] = []
    for label, start, goal in pairs:
        runs.extend(run_pair(grid, start, goal, label, repeats))
    return runs


def charger_pairs(grid: Grid) -> list[tuple[str, State, State]]:
    """Start/goal pairs from the environment file: charger -> each dirty cell.

    Taking pairs from ``grid`` keeps coordinates out of the code (AGENTS.md),
    and these are exactly the legs integration plans.

    Args:
        grid: Environment representation.

    Returns:
        ``(label, charger, cell)`` per dirty cell in file order.
    """
    return [(f"C->{lbl}", grid.charger, cell) for lbl, cell in grid.dirty.items()]


def open_grid(size: int) -> Grid:
    """Obstacle-free ``size`` x ``size`` grid for the scaling experiment.

    Args:
        size: Number of rows and columns.

    Returns:
        A grid with no obstacles or dirty cells.
    """
    return Grid(size, size, frozenset(), {}, (0, 0))


SCENARIOS = ("corner", "midline")


def scaling(
    sizes: Sequence[int], repeats: int = 3, scenario: str = "corner"
) -> list[Run]:
    """Runs on open grids of growing size.

    ``corner``: (0,0) -> opposite corner. Every cell inside the bounding box
    has the same f = g + h, so A* has nothing to prune and ties with UCS.
    ``midline``: left-edge midpoint -> right-edge midpoint; only cells on the
    straight line keep f minimal, which shows A*'s best case.

    Args:
        sizes: Grid side lengths to test.
        repeats: Timing repetitions per run.
        scenario: One of ``SCENARIOS``.

    Returns:
        Runs labelled ``"<n>x<n>"``.

    Raises:
        ValueError: If ``scenario`` is unknown.
    """
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario {scenario!r}; expected {SCENARIOS}")
    runs: list[Run] = []
    for n in sizes:
        if scenario == "corner":
            start, goal = (0, 0), (n - 1, n - 1)
        else:
            start, goal = (n // 2, 0), (n // 2, n - 1)
        runs.extend(run_pair(open_grid(n), start, goal, f"{n}x{n}", repeats))
    return runs


def format_table(runs: Sequence[Run], tablefmt: str = "github") -> str:
    """Render runs as an aligned table (spec §8.2 tabular comparison).

    Args:
        runs: Runs to show.
        tablefmt: ``tabulate`` format: ``"github"`` (Markdown, for the report
            files) or ``"grid"`` (plain text, for the notebook).

    Returns:
        Table text.
    """
    headers = [
        "Case",
        "Algorithm",
        "Start",
        "Goal",
        "Path cost",
        "Nodes expanded",
        "Time (ms)",
    ]
    rows = [
        [
            r.label,
            r.algorithm,
            str(r.start),
            str(r.goal),
            "no path" if r.cost is None else r.cost,
            r.nodes_expanded,
            f"{r.seconds * 1000:.3f}",
        ]
        for r in runs
    ]
    return tabulate(rows, headers=headers, tablefmt=tablefmt)
