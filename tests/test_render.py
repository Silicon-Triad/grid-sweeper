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
    assert "T4   | -" in text  # empty slot shown
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
