"""Unit tests for src/cep/csp.py (REQ-CSP-03..07, 11..18). Issues #17-#21."""

import itertools
import random
from pathlib import Path
from types import MappingProxyType

import pytest

from cep.csp import (
    backtracking_search,
    backtracking_search_with_stats,
    forward_check,
    is_consistent,
    order_domain_values,
    select_unassigned_variable,
)
from cep.env import (
    Constraints,
    initial_domains,
    load_environment,
    load_schedule,
    parse_schedule,
)

DATA = Path(__file__).resolve().parent.parent / "data"


def make(n_tasks, num_slots, precedence=(), latest=None):
    return Constraints(
        variables=tuple(f"D{i}" for i in range(1, n_tasks + 1)),
        num_slots=num_slots,
        precedence=tuple(precedence),
        latest=MappingProxyType(dict(latest or {})),
    )


def assert_valid(assignment, c):
    """Independent check of a full solution against every constraint."""
    assert set(assignment) == set(c.variables)  # every task gets one slot
    assert all(1 <= s <= c.num_slots for s in assignment.values())
    assert len(set(assignment.values())) == len(assignment)  # exclusivity
    for before, after in c.precedence:
        assert assignment[before] < assignment[after]
    for task, limit in c.latest.items():
        assert assignment[task] <= limit


def brute_force_feasible(c):
    """Oracle: try every injective slot assignment."""
    slots = range(1, c.num_slots + 1)
    for perm in itertools.permutations(slots, len(c.variables)):
        a = dict(zip(c.variables, perm, strict=True))
        if all(a[b] < a[x] for b, x in c.precedence) and all(
            a[t] <= limit for t, limit in c.latest.items()
        ):
            return True
    return False


# --- #19 is_consistent ----------------------------------------------------


def test_is_consistent_precedence():  # REQ-CSP-05
    c = make(2, 3, precedence=[("D1", "D2")])
    assert is_consistent("D2", 3, {"D1": 2}, c)
    assert not is_consistent("D2", 1, {"D1": 2}, c)
    # Checked from the other side too.
    assert is_consistent("D1", 1, {"D2": 2}, c)
    assert not is_consistent("D1", 3, {"D2": 2}, c)


def test_is_consistent_latest():  # REQ-CSP-06
    c = make(1, 4, latest={"D1": 2})
    assert is_consistent("D1", 2, {}, c)
    assert not is_consistent("D1", 3, {}, c)


def test_is_consistent_exclusive():  # REQ-CSP-07
    c = make(2, 3)
    assert not is_consistent("D2", 1, {"D1": 1}, c)
    assert is_consistent("D2", 2, {"D1": 1}, c)


def test_is_consistent_partial():  # REQ-CSP-15
    # D1 -> D2 cannot be judged until D1 is assigned.
    c = make(2, 3, precedence=[("D1", "D2")])
    assert is_consistent("D2", 1, {}, c)
    # The variable itself may already be in the assignment.
    assert is_consistent("D2", 3, {"D1": 1, "D2": 3}, c)


def test_is_consistent_self_precedence():  # REQ-CSP-05, DEC-12
    c = make(1, 3, precedence=[("D1", "D1")])
    assert not any(is_consistent("D1", s, {}, c) for s in (1, 2, 3))


# --- #17 select_unassigned_variable --------------------------------------


def test_select_mrv_degree():  # REQ-CSP-13
    c = make(3, 3, precedence=[("D2", "D3")])
    doms = initial_domains(c)
    # MRV: smallest domain wins regardless of degree or file order.
    doms["D3"] = [3]
    assert select_unassigned_variable({}, doms, c) == "D3"
    # Tie on MRV -> degree: D2 and D3 have degree 1, D1 has 0.
    doms = initial_domains(c)
    assert select_unassigned_variable({}, doms, c) == "D2"
    # Degree counts only unassigned neighbours: with D3 assigned, D2's degree
    # drops to 0 and file order picks D1.
    assert select_unassigned_variable({"D3": 3}, doms, c) == "D1"


def test_select_degree_counts_distinct_variables():  # DEC-05
    # D1 has two constraints but one neighbour (degree 1); D3 has two
    # neighbours (degree 2). Counting constraints would tie them and file
    # order would wrongly pick D1.
    c = make(5, 5, precedence=[("D1", "D2"), ("D2", "D1"), ("D3", "D4"), ("D3", "D5")])
    assert select_unassigned_variable({}, initial_domains(c), c) == "D3"


def test_select_file_order_tiebreak():  # DEC-05
    c = make(12, 12)
    assert select_unassigned_variable({}, initial_domains(c), c) == "D1"
    # Labels compared by file order, not as strings ("D10" < "D2").
    assigned = {f"D{i}": i for i in range(1, 10)}
    assert select_unassigned_variable(assigned, initial_domains(c), c) == "D10"


def test_select_all_assigned():
    c = make(2, 2)
    assert select_unassigned_variable({"D1": 1, "D2": 2}, initial_domains(c), c) is None


# --- #20 forward_check ----------------------------------------------------


def test_forward_check_prune_fail():  # REQ-CSP-16
    c = make(3, 3, precedence=[("D1", "D2")])
    doms = initial_domains(c)
    pruned = forward_check("D1", 2, {"D1": 2}, doms, c)
    assert pruned["D1"] == [2]
    assert pruned["D2"] == [3]  # after D1, and not slot 2
    assert pruned["D3"] == [1, 3]  # exclusivity only
    # D2 must come after D1 = 3: nothing left -> failure.
    assert forward_check("D1", 3, {"D1": 3}, doms, c) is None


def test_forward_check_restore():  # REQ-CSP-17
    c = make(3, 3, precedence=[("D1", "D2")])
    doms = initial_domains(c)
    before = {v: list(vals) for v, vals in doms.items()}
    forward_check("D1", 2, {"D1": 2}, doms, c)
    forward_check("D1", 3, {"D1": 3}, doms, c)  # failing call too
    assert doms == before


def test_backtracking_restores_after_failure(monkeypatch):  # REQ-CSP-17
    # Force the first forward check to fail, so the solver must backtrack.
    # The next value of the same variable must see the domains from before
    # the failed try, not a pruned copy.
    import cep.csp as csp

    real = csp.forward_check
    seen = []

    def failing_once(variable, value, assignment, domains, constraints):
        seen.append((variable, {v: list(d) for v, d in domains.items()}))
        if len(seen) == 1:
            return None
        return real(variable, value, assignment, domains, constraints)

    monkeypatch.setattr(csp, "forward_check", failing_once)
    c = make(3, 3, precedence=[("D1", "D2")])
    a = csp.backtracking_search(c.variables, initial_domains(c), c)
    assert_valid(a, c)
    (var1, doms1), (var2, doms2) = seen[0], seen[1]
    assert var1 == var2  # second value of the same variable
    assert doms1 == doms2  # removed values restored


# --- #18 order_domain_values ----------------------------------------------


def test_order_lcv():  # REQ-CSP-14
    c = make(2, 3, precedence=[("D1", "D2")])
    doms = initial_domains(c)
    # D1=1 rules out D2 slot 1 only; D1=2 rules out 1,2; D1=3 rules out all.
    assert order_domain_values("D1", {}, doms, c) == [1, 2, 3]
    # D2=3 rules out D1 slot 3 only; D2=1 rules out all of D1.
    assert order_domain_values("D2", {}, doms, c) == [3, 2, 1]


def test_order_lcv_keeps_ascending_on_ties():  # DEC-06
    c = make(2, 3)
    assert order_domain_values("D1", {}, initial_domains(c), c) == [1, 2, 3]


def test_order_returns_whole_domain():
    c = make(2, 4)
    doms = {"D1": [4, 2], "D2": [1, 2, 3]}
    assert sorted(order_domain_values("D1", {}, doms, c)) == [2, 4]


# --- #21 backtracking_search ----------------------------------------------


def test_backtracking_solves_sample():  # REQ-CSP-18, REQ-CSP-11
    grid = load_environment(DATA / "Environment_Sample.txt")
    c = load_schedule(DATA / "Schedule_Sample.txt", grid)
    a = backtracking_search(c.variables, initial_domains(c), c)
    assert a is not None
    assert_valid(a, c)


def test_backtracking_solves_own_schedule():  # REQ-CSP-11
    grid = load_environment(DATA / "Environment.txt")
    c = load_schedule(DATA / "Schedule.txt", grid)
    a = backtracking_search(c.variables, initial_domains(c), c)
    assert a is not None
    assert_valid(a, c)


def test_csp_unconstrained_tasks():  # REQ-CSP-03
    c = make(4, 4, precedence=[("D1", "D2")])
    a = backtracking_search(c.variables, initial_domains(c), c)
    assert set(a) == {"D1", "D2", "D3", "D4"}
    assert_valid(a, c)


def test_csp_solution_valid():  # REQ-CSP-11
    c = make(
        5,
        6,
        precedence=[("D1", "D2"), ("D2", "D3"), ("D4", "D3")],
        latest={"D3": 5, "D5": 1},
    )
    a = backtracking_search(c.variables, initial_domains(c), c)
    assert_valid(a, c)


@pytest.mark.parametrize(
    "c",
    [
        make(3, 3, precedence=[("D1", "D2"), ("D2", "D3"), ("D3", "D1")]),  # cycle
        make(2, 2, precedence=[("D1", "D1")]),  # self-precedence
        make(3, 3, latest={"D1": 1, "D2": 1}),  # two tasks need T1
        make(3, 4, precedence=[("D1", "D2"), ("D2", "D3")], latest={"D3": 2}),
    ],
    ids=["cycle", "self", "latest-clash", "chain-too-late"],
)
def test_csp_infeasible(c):  # REQ-CSP-12
    assert backtracking_search(c.variables, initial_domains(c), c) is None


def test_backtracking_does_not_modify_domains():
    c = make(3, 3, precedence=[("D1", "D2")], latest={"D3": 1})
    doms = initial_domains(c)
    backtracking_search(c.variables, doms, c)
    assert doms == initial_domains(c)


def test_backtracking_rejects_mismatched_variables():
    c = make(2, 2)
    with pytest.raises(ValueError):
        backtracking_search(("D1",), initial_domains(c), c)


def test_backtracking_matches_brute_force():  # REQ-CSP-09, REQ-CSP-11, REQ-CSP-12
    rng = random.Random(323)
    for _ in range(300):
        n = rng.randint(1, 5)
        slots = rng.randint(n, n + 2)
        labels = [f"D{i}" for i in range(1, n + 1)]
        prec = {
            (rng.choice(labels), rng.choice(labels)) for _ in range(rng.randint(0, 4))
        }
        latest = {
            t: rng.randint(1, slots) for t in rng.sample(labels, rng.randint(0, n))
        }
        c = make(n, slots, sorted(prec), latest)
        a = backtracking_search(c.variables, initial_domains(c), c)
        assert (a is not None) == brute_force_feasible(c), c
        if a is not None:
            assert_valid(a, c)


# --- Backtracking stats and demo (REQ-CSP-17, REQ-CSP-18, DEC-16, #70) ---


# Smallest feasible schedule found on our own grid (5 tasks) that makes the
# solver hit a dead end after recursing; same text as the notebook demo.
DEMO_SCHEDULE = "5\n3\n(D1,D2)\n(D3,D1)\n(D5,D3)\n0\n"


def _solve_with_stats(c):
    return backtracking_search_with_stats(list(c.variables), initial_domains(c), c)


def test_csp_demo_schedule_backtracks_and_is_valid():
    grid = load_environment(DATA / "Environment.txt")
    c = parse_schedule(DEMO_SCHEDULE, grid)
    assignment, stats = _solve_with_stats(c)
    assert assignment is not None
    assert_valid(assignment, c)
    assert stats["backtracks"] >= 1
    assert stats["values_restored"] >= 1


def test_csp_stats_invariants_on_random_problems():
    rng = random.Random(70)
    for _ in range(300):
        n = rng.randint(2, 5)
        slots = rng.randint(n, n + 2)
        labels = [f"D{i}" for i in range(1, n + 1)]
        pairs = list(itertools.permutations(labels, 2))
        prec = rng.sample(pairs, rng.randint(0, min(3, len(pairs))))
        latest = {
            t: rng.randint(1, slots) for t in rng.sample(labels, rng.randint(0, 2))
        }
        c = make(n, slots, prec, latest)
        assignment, stats = _solve_with_stats(c)
        # Restored values are a subset of pruned ones, and only an abandoned
        # branch (a backtrack) gives values back (REQ-CSP-17).
        assert 0 <= stats["values_restored"] <= stats["values_pruned"]
        assert (stats["values_restored"] > 0) <= (stats["backtracks"] > 0)
        assert stats["fc_rejections"] <= stats["assignments_tried"]
        assert stats["backtracks"] <= stats["assignments_tried"]
        if assignment is not None:
            assert_valid(assignment, c)
            # One kept assignment per variable on the successful path.
            assert stats["assignments_tried"] - stats["fc_rejections"] - (
                stats["backtracks"]
            ) == len(labels)
        assert assignment == backtracking_search(
            list(c.variables), initial_domains(c), c
        )


@pytest.mark.parametrize(
    "env, sched",
    [
        ("Environment.txt", "Schedule.txt"),
        ("Environment_Sample.txt", "Schedule_Sample.txt"),
    ],
)
def test_csp_stats_version_matches_frozen(env, sched):
    grid = load_environment(DATA / env)
    c = load_schedule(DATA / sched, grid)
    frozen = backtracking_search(list(c.variables), initial_domains(c), c)
    with_stats, _ = _solve_with_stats(c)
    assert frozen is not None
    assert with_stats == frozen
