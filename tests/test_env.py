from collections import deque
from pathlib import Path

import pytest

from cep.env import InputError, load_environment, parse_environment

SAMPLE_ENV = """4,4
2
(1,1) (2,2)
2
(0,1) (3,2)
(0,0)
"""

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


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
    free_cells = grid.rows * grid.cols - len(grid.obstacles)
    assert free_cells == 14
    assert grid.charger not in grid.obstacles
    assert all(cell not in grid.obstacles for cell in grid.dirty.values())


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
    grid = load_environment(DATA / "Environment.txt")
    assert grid.rows >= 8
    assert grid.cols >= 8
    assert len(grid.obstacles) >= 6
    assert len(grid.dirty) >= 4


def test_env_own_reachable():
    grid = load_environment(DATA / "Environment.txt")
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

    dirty_cells = list(grid.dirty.values())

    assert grid.charger not in grid.obstacles
    assert grid.charger not in dirty_cells
    assert len(dirty_cells) == len(set(dirty_cells))
    assert set(dirty_cells).isdisjoint(grid.obstacles)

    for dirty_position in dirty_cells:
        assert dirty_position in visited


def test_env_loads_real_sample_file():
    grid = load_environment(DATA / "Environment_Sample.txt")
    assert grid.rows == 8
    assert grid.cols == 8
    assert len(grid.obstacles) == 6
    assert len(grid.dirty) == 4
    assert grid.charger == (0, 0)


def test_env_rejects_invalid_environment_file(tmp_path):
    error_file = tmp_path / "Environment_Error.txt"
    error_file.write_text(
        """4,4
1
(5,1)
0

(0,0)
""",
        encoding="utf-8",
    )

    with pytest.raises(InputError):
        load_environment(error_file)


# --- Input tolerance (DEC-08, DEC-11, DEC-12 revised #70; REQ-ENV-02, REQ-CSP-02)

OWN_SCHEDULE_TEXT = (DATA / "Schedule.txt").read_text(encoding="utf-8")


def _spread_blank_lines(text: str) -> str:
    """Put a blank and a whitespace-only line between every pair of lines."""
    return "\n \t\n\n".join(text.splitlines()) + "\n\n"


def test_env_blank_lines_everywhere_parse_like_compact():
    from cep.env import parse_schedule

    compact = (DATA / "Environment.txt").read_text(encoding="utf-8")
    grid = parse_environment(compact)
    spread = parse_environment("\n\n" + _spread_blank_lines(compact))
    assert spread == grid
    assert parse_schedule(_spread_blank_lines(OWN_SCHEDULE_TEXT), grid) == (
        parse_schedule(OWN_SCHEDULE_TEXT, grid)
    )


def test_env_zero_count_with_or_without_empty_line():
    with_line = "4,4\n0\n\n0\n\n(0,0)\n"
    without = "4,4\n0\n0\n(0,0)\n"
    assert parse_environment(with_line) == parse_environment(without)


def test_schedule_duplicate_latest_keeps_tighter_slot():
    from cep.env import parse_schedule

    grid = parse_environment(SAMPLE_ENV)
    text = "4\n0\n3\n(D1,T4)\n(D1,T2)\n(D1,T3)\n"
    assert parse_schedule(text, grid).latest == {"D1": 2}


def test_schedule_duplicate_latest_still_checks_range_and_label():
    from cep.env import parse_schedule

    grid = parse_environment(SAMPLE_ENV)
    with pytest.raises(InputError, match="outside"):
        parse_schedule("4\n0\n2\n(D1,T2)\n(D1,T9)\n", grid)
    with pytest.raises(InputError, match="unknown task"):
        parse_schedule("4\n0\n2\n(D1,T2)\n(D7,T2)\n", grid)


def test_env_dirty_on_charger_cites_spec_section_4():
    text = "4,4\n0\n1\n(0,0)\n(0,0)\n"
    with pytest.raises(InputError, match="§4"):
        parse_environment(text)
