"""Unit tests for src/cep/search.py (REQ-SRCH-01..14, REQ-CMP-01). Issues #11-#14."""

from collections import deque
from pathlib import Path

import pytest

from cep.env import ALGORITHMS, Grid, load_environment
from cep.search import get_successors, goal_test, heuristic, path_cost, search

DATA = Path(__file__).resolve().parent.parent / "data"


def make_grid(rows, cols, obstacles=()):
    # dirty/charger are irrelevant to search; both are passable cells.
    return Grid(rows, cols, frozenset(obstacles), {}, (0, 0))


def bfs_distance(grid, start, goal):
    """Independent oracle for optimal cost on a unit-cost grid."""
    seen, queue = {start: 0}, deque([start])
    while queue:
        s = queue.popleft()
        if s == goal:
            return seen[s]
        for n, _, _ in get_successors(s, grid):
            if n not in seen:
                seen[n] = seen[s] + 1
                queue.append(n)
    return None


def assert_valid_path(grid, path, start, goal):
    assert path[0] == start and path[-1] == goal
    for a, b in zip(path, path[1:], strict=False):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
        assert 0 <= b[0] < grid.rows and 0 <= b[1] < grid.cols
        assert b not in grid.obstacles


# --- #11 ------------------------------------------------------------------


def test_successors_actions():  # REQ-SRCH-02
    succ = get_successors((1, 1), make_grid(3, 3))
    assert [(s, a) for s, a, _ in succ] == [
        ((0, 1), "UP"),
        ((2, 1), "DOWN"),
        ((1, 0), "LEFT"),
        ((1, 2), "RIGHT"),
    ]


def test_successors_bounds_obstacles():  # REQ-SRCH-03
    assert [a for _, a, _ in get_successors((0, 0), make_grid(3, 3))] == [
        "DOWN",
        "RIGHT",
    ]
    grid = make_grid(3, 3, {(0, 1), (1, 0)})
    assert get_successors((0, 0), grid) == []
    assert get_successors((0, 0), make_grid(1, 1)) == []


def test_successors_cost():  # REQ-SRCH-04
    assert all(c == 1 for _, _, c in get_successors((1, 1), make_grid(3, 3)))


def test_goal_test():  # REQ-SRCH-05
    assert goal_test((2, 3), (2, 3))
    assert not goal_test((2, 3), (3, 2))


def test_path_cost_edges():  # REQ-SRCH-06, DEC-04
    assert path_cost([]) == 0
    assert path_cost([(0, 0)]) == 0
    assert path_cost([(0, 0), (0, 1), (1, 1)]) == 2


def test_heuristic_manhattan():  # REQ-SRCH-07
    assert heuristic((0, 0), (0, 0)) == 0
    assert heuristic((1, 5), (4, 2)) == 6
    assert heuristic((4, 2), (1, 5)) == 6


# --- #12 / #13 ------------------------------------------------------------


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_search_returns(algorithm):  # REQ-SRCH-09
    grid = make_grid(3, 3, {(1, 1)})
    path, cost, expanded = search(grid, (0, 0), (2, 2), algorithm)
    assert cost == 4 == path_cost(path)
    assert_valid_path(grid, path, (0, 0), (2, 2))
    assert isinstance(expanded, int) and expanded > 0


def test_search_unknown_algorithm():  # DEC-06
    with pytest.raises(ValueError):
        search(make_grid(2, 2), (0, 0), (1, 1), "bfs")


def test_search_algorithms():  # REQ-SRCH-01: heuristic guides A*, same cost
    grid = make_grid(10, 10)
    _, c_u, n_u = search(grid, (0, 0), (0, 9), "ucs")
    _, c_a, n_a = search(grid, (0, 0), (0, 9), "astar")
    assert c_u == c_a == 9
    assert n_a == 9  # only row 0 has f == 9; every other cell has f > 9
    assert n_a < n_u


def test_search_arbitrary_pairs():  # REQ-SRCH-10, REQ-SRCH-12, REQ-CMP-01
    grid = load_environment(DATA / "Environment.txt")
    free = [
        (r, c)
        for r in range(grid.rows)
        for c in range(grid.cols)
        if (r, c) not in grid.obstacles
    ]
    for start in free[::7]:
        for goal in free[::5]:
            best = bfs_distance(grid, start, goal)
            for algorithm in ALGORITHMS:
                path, cost, _ = search(grid, start, goal, algorithm)
                if best is None:
                    assert path is None and cost is None
                else:
                    assert cost == best
                    assert_valid_path(grid, path, start, goal)


def test_search_same_problem():  # REQ-SRCH-11, REQ-CMP-01
    grid = load_environment(DATA / "Environment.txt")
    results = [search(grid, grid.charger, grid.dirty["D3"], a) for a in ALGORITHMS]
    assert len({cost for _, cost, _ in results}) == 1
    assert all(path is not None for path, _, _ in results)


def test_search_same_cost():  # REQ-CMP-01
    grid = make_grid(6, 6, {(1, 1), (2, 2), (3, 3), (1, 3), (3, 1)})
    costs = {search(grid, (0, 0), (5, 5), a)[1] for a in ALGORITHMS}
    assert costs == {10}


# --- #14 ------------------------------------------------------------------


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_search_start_equals_goal(algorithm):  # REQ-SRCH-13
    assert search(make_grid(3, 3), (1, 1), (1, 1), algorithm) == ([(1, 1)], 0, 0)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_search_no_path(algorithm):  # REQ-SRCH-14
    grid = make_grid(3, 3, {(0, 2), (1, 2), (2, 2)})  # wall cuts off column 2
    path, cost, expanded = search(grid, (0, 0), (1, 2), algorithm)
    assert (path, cost) == (None, None)
    assert expanded == 6  # every reachable cell expanded once


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_search_error_file_unreachable(algorithm):  # REQ-SRCH-14, #10
    grid = load_environment(DATA / "Environment_Error.txt")
    unreachable = [
        lbl
        for lbl, cell in grid.dirty.items()
        if bfs_distance(grid, grid.charger, cell) is None
    ]
    assert unreachable
    for lbl in unreachable:
        assert search(grid, grid.charger, grid.dirty[lbl], algorithm)[:2] == (
            None,
            None,
        )
