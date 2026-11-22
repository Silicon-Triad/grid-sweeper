"""Unit tests for src/cep/render.py. Issue #22 (REQ-CSP-19)."""

from pathlib import Path
from types import MappingProxyType

from cep.csp import backtracking_search
from cep.env import Constraints, initial_domains, load_environment, load_schedule
from cep.render import check_schedule, format_schedule, format_schedule_proof

DATA = Path(__file__).resolve().parent.parent / "data"

C = Constraints(("D1", "D2", "D3"), 4, (("D1", "D3"),), MappingProxyType({"D2": 2}))


def test_schedule_proof_satisfied():
    a = {"D1": 1, "D2": 2, "D3": 3}
    checks = check_schedule(a, C)
    assert all(c.ok for c in checks)
    text = format_schedule_proof(a, C)
    assert "D1 (T1) before D3 (T3) ✓" in text
    assert "D2 ≤ T2: T2 ✓" in text
    assert "| T4     | -      |" in text  # empty slot shown
    assert "all constraints satisfied" in text


def test_schedule_proof_violated():
    a = {"D1": 3, "D2": 3, "D3": 1}
    bad = {c.kind for c in check_schedule(a, C) if not c.ok}
    assert bad == {"precedence", "latest", "exclusivity"}
    text = format_schedule_proof(a, C)
    assert "D1 (T3) before D3 (T1) ✗" in text and "VIOLATED" in text


def test_schedule_proof_missing_task():
    checks = check_schedule({"D1": 1, "D2": 2}, C)
    assert [c.kind for c in checks if not c.ok] == ["assigned", "precedence"]


def test_schedule_proof_no_schedule():
    assert "No feasible schedule" in format_schedule_proof(None, C)


def test_slot_table_numeric_order():
    text = format_schedule({f"D{i}": i for i in range(1, 11)}, 10)
    assert text.index("T9 ") < text.index("T10")


def test_schedule_proof_data_files():
    for env, sched in [
        ("Environment.txt", "Schedule.txt"),
        ("Environment_Sample.txt", "Schedule_Sample.txt"),
    ]:
        g = load_environment(DATA / env)
        c = load_schedule(DATA / sched, g)
        a = backtracking_search(list(c.variables), initial_domains(c), c)
        assert all(ch.ok for ch in check_schedule(a, c))


# --- #24 integration display (REQ-INT-08) ---
from cep.env import Grid  # noqa: E402
from cep.integrate import plan_and_execute, run_integration  # noqa: E402
from cep.render import format_grid, format_result  # noqa: E402


def tiny(obstacles=()):
    return Grid(2, 3, frozenset(obstacles), MappingProxyType({"D1": (0, 2)}), (0, 0))


def test_format_grid_symbols():
    g = tiny(obstacles=[(1, 1)])
    assert format_grid(g).splitlines() == [
        "+----+-----+-----+-----+",
        "|    |  0  |  1  |  2  |",
        "+====+=====+=====+=====+",
        "|  0 |  C  |  .  | D1  |",
        "+----+-----+-----+-----+",
        "|  1 |  .  | ##  |  .  |",
        "+----+-----+-----+-----+",
    ]
    text = format_grid(g, [(0, 0), (0, 1), (0, 2)], ["D1"])
    assert text.splitlines()[3] == "|  0 |  C  |  *  | d1  |"


def test_format_grid_columns_align_with_two_digit_labels():
    dirty = {f"D{i}": (0, i - 1) for i in range(1, 12)}
    g = Grid(1, 11, frozenset(), MappingProxyType(dirty), (0, 0))
    lines = format_grid(g).splitlines()
    assert len({len(line) for line in lines}) == 1  # every row equally wide


def test_format_result_success():
    g = tiny()
    text = format_result(run_integration(g, g.charger, ["D1"], "ucs"), g)
    assert "Visit sequence: C -> D1 -> C" in text
    assert "Leg 1: C (0, 0) -> D1 (0, 2): cost 2, nodes expanded" in text
    assert "Total moves: 4, total cost: 4" in text
    assert "Status: SUCCESS" in text


def test_format_result_failure():
    g = tiny(obstacles=[(0, 1), (1, 1)])
    text = format_result(run_integration(g, g.charger, ["D1"], "astar"), g)
    assert "NO PATH" in text and "Status: FAILURE: no path from C" in text
    assert "SUCCESS" not in text


def test_format_result_data_files():
    g = load_environment(DATA / "Environment.txt")
    c = load_schedule(DATA / "Schedule.txt", g)
    text = format_result(plan_and_execute(g, c, "astar"), g)
    assert "Schedule: T1:D1, T2:D2" in text and "Status: SUCCESS" in text
