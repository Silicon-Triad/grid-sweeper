from pathlib import Path

import pytest
from src.cep.env import InputError, parse_environment

SAMPLE_ENV = """4,4
2
(1,1) (2,2)
2
(0,1) (3,2)
(0,0)
"""


def test_env_parse_sample():
    grid = parse_environment(SAMPLE_ENV)

    assert grid.rows == 4
    assert grid.cols == 4
    assert len(grid.obstacles) == 2
    assert len(grid.dirty) == 2
    assert grid.charger == (0, 0)


def test_env_coordinates():
    grid = parse_environment(SAMPLE_ENV)

    assert (1, 1) in grid.obstacles
    assert (2, 2) in grid.obstacles
    assert grid.dirty["D1"] == (0, 1)
    assert grid.dirty["D2"] == (3, 2)


def test_env_labels():
    grid = parse_environment(SAMPLE_ENV)

    assert list(grid.dirty.keys()) == ["D1", "D2"]


def test_env_grid_cells():
    grid = parse_environment(SAMPLE_ENV)

    assert grid.rows == 4
    assert grid.cols == 4
    assert grid.charger == (0, 0)


def test_env_rejects_negative_dimensions():
    text = """-4,4
0

0

(0,0)
"""
    with pytest.raises(InputError):
        parse_environment(text)


def test_env_rejects_out_of_bounds_coordinates():
    text = """4,4
1
(5,1)
0

(0,0)
"""
    with pytest.raises(InputError):
        parse_environment(text)


def test_env_rejects_duplicate_obstacles():
    text = """4,4
2
(1,1) (1,1)
0

(0,0)
"""
    with pytest.raises(InputError):
        parse_environment(text)


def test_env_rejects_overlap():
    text = """4,4
1
(1,1)
1
(1,1)
(0,0)
"""
    with pytest.raises(InputError):
        parse_environment(text)


def test_env_rejects_missing_data():
    text = """4,4
1
(1,1)
"""
    with pytest.raises(InputError):
        parse_environment(text)


def test_env_rejects_extra_data():
    text = """4,4
0

0

(0,0)
EXTRA
"""
    with pytest.raises(InputError):
        parse_environment(text)


def test_env_zero_obstacles_and_dirty():
    text = """4,4
0

0

(0,0)
"""
    grid = parse_environment(text)

    assert len(grid.obstacles) == 0
    assert len(grid.dirty) == 0


def test_env_own_minimums():
    env_path = Path(__file__).resolve().parent.parent / "Environment.txt"
    grid = parse_environment(env_path.read_text(encoding="utf-8"))

    assert grid.rows >= 8
    assert grid.cols >= 8
    assert len(grid.obstacles) >= 6
    assert len(grid.dirty) >= 4


def test_env_own_reachable():
    from collections import deque

    env_path = Path(__file__).resolve().parent.parent / "Environment.txt"
    grid = parse_environment(env_path.read_text(encoding="utf-8"))

    start = grid.charger
    visited = {start}
    queue = deque([start])

    while queue:
        row, col = queue.popleft()

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_cell = (row + dr, col + dc)

            if (
                0 <= next_cell[0] < grid.rows
                and 0 <= next_cell[1] < grid.cols
                and next_cell not in grid.obstacles
                and next_cell not in visited
            ):
                visited.add(next_cell)
                queue.append(next_cell)

    for dirty_position in grid.dirty.values():
        assert dirty_position in visited
