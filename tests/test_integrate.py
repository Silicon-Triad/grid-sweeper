"""Unit tests for src/cep/integrate.py (REQ-INT-01..07, 09). Issue #23."""

from pathlib import Path
from types import MappingProxyType

import pytest

import cep.integrate as integrate
from cep.env import (
    ALGORITHMS,
    Constraints,
    Grid,
    load_environment,
    load_schedule,
    parse_schedule,
)
from cep.integrate import (
    execute_schedule,
    plan_and_execute,
    run_integration,
    schedule_from_assignment,
)

DATA = Path(__file__).resolve().parent.parent / "data"


def grid(rows, cols, obstacles=(), dirty=(), charger=(0, 0)):
    labels = {f"D{i}": c for i, c in enumerate(dirty, start=1)}
    return Grid(rows, cols, frozenset(obstacles), MappingProxyType(labels), charger)


def adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


def test_integrate_order():
    # Numeric slot order: T10 after T9 (a string sort would get this wrong).
    assignment = {"D1": 10, "D2": 9, "D3": 1}
    assert schedule_from_assignment(assignment) == ["D3", "D2", "D1"]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_integrate_starts_at_charger(algorithm):
    g = grid(3, 3, dirty=[(2, 2), (0, 2)], charger=(1, 0))
    path, _, _ = execute_schedule(g, g.charger, ["D1", "D2"], algorithm)
    assert path[0] == g.charger


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_integrate_returns(algorithm):
    g = grid(3, 3, dirty=[(2, 2), (0, 2)], charger=(1, 0))
    path, cost, success = execute_schedule(g, g.charger, ["D1", "D2"], algorithm)
    assert success and path[-1] == g.charger
    # Visits in schedule order: D1 before D2.
    assert path.index((2, 2)) < path.index((0, 2))
    assert cost == len(path) - 1


def test_integrate_marks_cleaned():
    g = grid(3, 3, dirty=[(2, 2), (0, 2)])
    result = run_integration(g, g.charger, ["D2", "D1"], "ucs")
    assert result.cleaned == ["D2", "D1"]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_integrate_no_duplicate_joints(algorithm):
    g = grid(4, 4, obstacles=[(1, 1)], dirty=[(3, 3), (0, 3)])
    path, cost, _ = execute_schedule(g, g.charger, ["D1", "D2"], algorithm)
    # Every consecutive pair is one move: no repeated joint, no jumps.
    assert all(adjacent(a, b) for a, b in zip(path, path[1:], strict=False))
    result = run_integration(g, g.charger, ["D1", "D2"], algorithm)
    assert cost == sum(leg.cost for leg in result.legs)


def test_integrate_empty_schedule():
    g = grid(2, 2)
    assert execute_schedule(g, g.charger, [], "ucs") == ([(0, 0)], 0, True)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_integrate_failure(algorithm):
    # D2 at (2,2) is walled off by (1,2) and (2,1).
    g = grid(3, 3, obstacles=[(1, 2), (2, 1)], dirty=[(0, 2), (2, 2)])
    path, cost, success = execute_schedule(g, g.charger, ["D1", "D2"], algorithm)
    assert success is False
    # DEC-15: the part walked so far (charger -> D1) is returned.
    assert path == [(0, 0), (0, 1), (0, 2)] and cost == 2
    result = run_integration(g, g.charger, ["D1", "D2"], algorithm)
    assert result.cleaned == ["D1"]
    assert result.legs[-1].path is None
    assert "D2" in result.reason


def test_integrate_failure_own_error_file():
    g = load_environment(DATA / "Environment_Error.txt")
    c = load_schedule(DATA / "Schedule_Error.txt", g)
    for algorithm in ALGORITHMS:
        result = plan_and_execute(g, c, algorithm)
        assert result.success is False and result.reason


def test_integrate_infeasible_schedule_reports_failure(monkeypatch):
    g = grid(3, 3, dirty=[(0, 2), (2, 2)])
    c = Constraints(("D1", "D2"), 2, (("D1", "D2"), ("D2", "D1")), MappingProxyType({}))
    calls = []
    monkeypatch.setattr(integrate, "search", lambda *a: calls.append(a))
    result = plan_and_execute(g, c, "ucs")
    assert result.success is False and "schedule" in result.reason
    assert calls == []  # no search when the CSP fails


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_integrate_returns_tuple(algorithm):
    g = load_environment(DATA / "Environment.txt")
    c = load_schedule(DATA / "Schedule.txt", g)
    schedule = plan_and_execute(g, c, algorithm).schedule
    out = execute_schedule(g, g.charger, schedule, algorithm)
    assert isinstance(out, tuple) and len(out) == 3
    path, cost, success = out
    assert isinstance(path, list) and isinstance(cost, int) and success is True


@pytest.mark.parametrize(
    "env,sched",
    [
        ("Environment.txt", "Schedule.txt"),
        ("Environment_Sample.txt", "Schedule_Sample.txt"),
    ],
)
def test_integrate_uses_components(monkeypatch, env, sched):
    g = load_environment(DATA / env)
    c = load_schedule(DATA / sched, g)
    real_search = integrate.search
    calls = []

    def spy(grid_, start, goal, algorithm):
        calls.append((start, goal))
        return real_search(grid_, start, goal, algorithm)

    monkeypatch.setattr(integrate, "search", spy)
    result = plan_and_execute(g, c, "astar")
    assert result.success
    # Schedule comes from the real CSP assignment, sorted by slot.
    assert result.schedule == sorted(result.assignment, key=result.assignment.get)
    # One search per task plus the return leg, chained position to position.
    stops = [g.dirty[x] for x in result.schedule] + [g.charger]
    assert calls == list(zip([g.charger] + stops[:-1], stops, strict=True))


def test_integrate_real_csp_infeasible_run():
    """Real solver, no stubbing: a precedence cycle has no schedule (#70).

    REQ-INT-07, REQ-CSP-12: failure is reported, no search runs (no legs),
    and the robot never leaves the charger.
    """
    grid = load_environment(DATA / "Environment.txt")
    constraints = parse_schedule("5\n2\n(D1,D2)\n(D2,D1)\n0\n", grid)
    for algorithm in ALGORITHMS:
        result = integrate.plan_and_execute(grid, constraints, algorithm)
        assert result.success is False
        assert result.reason == "CSP solver found no feasible schedule"
        assert result.schedule == []
        assert result.legs == []
        assert result.cleaned == []
        assert result.complete_path == [grid.charger]
        assert result.total_cost == 0
