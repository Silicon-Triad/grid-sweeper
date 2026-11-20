"""Tests for src/cep/compare.py (REQ-CMP-01, REQ-CMP-02). Issue #16."""

from pathlib import Path

from cep.compare import charger_pairs, compare_pairs, format_table, scaling
from cep.env import ALGORITHMS, load_environment

DATA = Path(__file__).resolve().parent.parent / "data"


def test_pairs_same_cost_astar_fewer_nodes():  # REQ-CMP-01
    grid = load_environment(DATA / "Environment.txt")
    pairs = charger_pairs(grid)
    assert len(pairs) >= 3
    runs = compare_pairs(grid, pairs)
    assert len(runs) == len(pairs) * len(ALGORITHMS)
    for i in range(0, len(runs), len(ALGORITHMS)):
        ucs, astar = runs[i], runs[i + 1]
        assert ucs.cost == astar.cost
        assert astar.nodes_expanded <= ucs.nodes_expanded


def test_scaling_and_table():  # REQ-CMP-02
    runs = scaling([3, 6], repeats=1)
    assert [r.cost for r in runs] == [4, 4, 10, 10]
    table = format_table(runs)
    assert "3x3" in table and "astar" in table


def test_midline_astar_expands_only_the_line():  # REQ-CMP-02
    runs = scaling([7], repeats=1, scenario="midline")
    ucs, astar = runs
    assert ucs.cost == astar.cost == 6
    assert astar.nodes_expanded == 6 < ucs.nodes_expanded
