"""Property-based tests for the environment and schedule generator.

Covers REQ-TEST and REQ-ENV-05. Issue #6.
"""

import random

from hypothesis import given, settings
from hypothesis import strategies as st
from tools.gen_env import make_environment, make_schedule

from cep.env import parse_environment, parse_schedule


@settings(max_examples=50, deadline=None)
@given(
    rows=st.integers(min_value=3, max_value=10),
    cols=st.integers(min_value=3, max_value=10),
    dirt_count=st.integers(min_value=1, max_value=4),
    seed=st.integers(),
)
def test_reachable_environment_properties(rows, cols, dirt_count, seed):
    """Generated reachable environments must pass the environment parser."""
    obstacle_count = min(3, rows * cols - dirt_count - 1)
    rng = random.Random(seed)

    environment = make_environment(rng, rows, cols, obstacle_count, dirt_count, False)

    grid = parse_environment(environment, source="property-test environment")

    assert grid.rows == rows
    assert grid.cols == cols
    assert len(grid.dirty) == dirt_count
    assert len(grid.obstacles) == obstacle_count
    assert grid.charger not in grid.obstacles


@settings(max_examples=50, deadline=None)
@given(
    rows=st.integers(min_value=3, max_value=10),
    cols=st.integers(min_value=3, max_value=10),
    dirt_count=st.integers(min_value=1, max_value=4),
    seed=st.integers(),
)
def test_unreachable_environment_properties(rows, cols, dirt_count, seed):
    """Unreachable environments must contain an isolated dirty cell."""
    obstacle_count = min(4, rows * cols - dirt_count - 1)
    obstacle_count = max(2, obstacle_count)
    rng = random.Random(seed)

    environment = make_environment(rng, rows, cols, obstacle_count, dirt_count, True)

    grid = parse_environment(environment, source="property-test unreachable")

    assert grid.rows == rows
    assert grid.cols == cols
    assert len(grid.dirty) == dirt_count
    assert len(grid.obstacles) == obstacle_count
    assert grid.charger not in grid.obstacles

    isolated_cells = [
        cell
        for cell in grid.dirty.values()
        if all(
            neighbour in grid.obstacles
            for neighbour in (
                (cell[0] - 1, cell[1]),
                (cell[0] + 1, cell[1]),
                (cell[0], cell[1] - 1),
                (cell[0], cell[1] + 1),
            )
            if 0 <= neighbour[0] < rows and 0 <= neighbour[1] < cols
        )
    ]

    assert isolated_cells


@settings(max_examples=50, deadline=None)
@given(
    dirt_count=st.integers(min_value=1, max_value=8),
    seed=st.integers(),
)
def test_feasible_schedule_properties(dirt_count, seed):
    """Generated feasible schedules must pass the schedule parser."""
    rng = random.Random(seed)
    schedule = make_schedule(rng, dirt_count, False)

    environment = make_environment(
        random.Random(seed),
        4,
        4,
        0,
        dirt_count,
        False,
    )
    grid = parse_environment(environment, source="property-test schedule")

    parse_schedule(schedule, grid, source="property-test feasible schedule")


@settings(max_examples=50, deadline=None)
@given(
    dirt_count=st.integers(min_value=1, max_value=8),
    seed=st.integers(),
)
def test_infeasible_schedule_properties(dirt_count, seed):
    """Generated infeasible schedules must pass the schedule parser."""
    rng = random.Random(seed)
    schedule = make_schedule(rng, dirt_count, True)

    environment = make_environment(
        random.Random(seed),
        4,
        4,
        0,
        dirt_count,
        False,
    )
    grid = parse_environment(environment, source="property-test schedule")

    parse_schedule(schedule, grid, source="property-test infeasible schedule")
