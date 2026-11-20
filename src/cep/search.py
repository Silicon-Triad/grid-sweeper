"""Graph-based search for robot navigation (spec §5). Owner: Mujtaba.

Spec §5.3: "State: Represent the robot's position as (row,column)." /
"Actions: UP, DOWN, LEFT, and RIGHT. An action is valid only if the resulting
cell is within the grid boundaries and is not an obstacle." / "Step cost: Each
valid movement has a cost of 1."

Frozen interface: see docs/plan.md §4 and AGENTS.md.

UCS and A* share one best-first graph search (DEC-01); A* only adds the
heuristic to the priority (REQ-SRCH-01).
"""

import heapq
from collections.abc import Sequence
from itertools import count

from cep.env import ACTIONS, ALGORITHMS, Grid, State

# Spec §5.3: "Each valid movement has a cost of 1."
STEP_COST = 1


def get_successors(state: State, grid: Grid) -> list[tuple[State, str, int]]:
    """Find all valid successor states (spec §5.5).

    Spec: "Find all valid successor states without including cells outside
    the grid or obstacle cells."

    Args:
        state: Current robot position.
        grid: Environment representation.

    Returns:
        A list of valid successors, each represented as
        (next_state, action, step_cost).
    """
    row, col = state
    successors = []
    # ACTIONS order fixes successor order and hence tie-breaks (REQ-SRCH-02).
    for action, (dr, dc) in ACTIONS:
        nxt = (row + dr, col + dc)
        in_bounds = 0 <= nxt[0] < grid.rows and 0 <= nxt[1] < grid.cols
        if in_bounds and nxt not in grid.obstacles:
            successors.append((nxt, action, STEP_COST))
    return successors


def goal_test(state: State, goal_state: State) -> bool:
    """Check whether the goal has been reached (spec §5.5).

    Args:
        state: Current robot position.
        goal_state: Target position.

    Returns:
        True if state equals goal_state; otherwise, False.
    """
    return state == goal_state


def path_cost(path: Sequence[State]) -> int:
    """Calculate the total cost of a path (spec §5.5).

    Spec: "Since each movement costs 1, the path cost equals the number of
    movements, or the number of states in the path minus one. An empty path
    and a path containing only the initial state must be handled
    appropriately."

    Args:
        path: Sequence of states from the start to the goal.

    Returns:
        Total path cost.
    """
    # DEC-04: [] -> 0 (team choice); a single-state path has no moves.
    if not path:
        return 0
    return (len(path) - 1) * STEP_COST


def heuristic(state: State, goal_state: State) -> int:
    """Estimate the cost from the current state to the goal (spec §5.5).

    Spec: "For four-directional movement, students may use Manhattan distance:
    h(n) = |row_n - row_goal| + |col_n - col_goal|. Students must explain why
    their selected heuristic is appropriate for the environment and search
    algorithm."

    Args:
        state: Current robot position.
        goal_state: Target position.

    Returns:
        An estimate of the cost from the current state to the goal.
    """
    # Manhattan distance (DEC-02): admissible and consistent for 4-way unit
    # moves, since each move changes |dr| + |dc| by exactly 1 (REQ-SRCH-08).
    return abs(state[0] - goal_state[0]) + abs(state[1] - goal_state[1])


def search(
    grid: Grid, start: State, goal: State, algorithm: str
) -> tuple[list[State] | None, int | None, int]:
    """Implement the selected search algorithm (spec §5.5).

    Spec §5.4: "The start and goal positions must be provided as inputs rather
    than hardcoded in the search algorithm." / "The program must correctly
    handle cases where the start equals the goal or no path exists."

    Args:
        grid: Environment representation.
        start: Starting position.
        goal: Target position.
        algorithm: Selected graph-search algorithm, one of ``ALGORITHMS``.

    Returns:
        path: Sequence of states from start to goal, or None if no path
            exists.
        cost: Total path cost if a path is found, otherwise None.
        nodes_expanded: Number of nodes expanded during the search.

    Raises:
        ValueError: If ``algorithm`` is not in ``ALGORITHMS``.
    """
    if algorithm not in ALGORITHMS:
        # DEC-06: a typo must not look like "no path exists".
        raise ValueError(
            f"unknown algorithm {algorithm!r}; expected one of {ALGORITHMS}"
        )
    use_h = algorithm == "astar"

    def priority(state: State, g: int) -> int:
        return g + heuristic(state, goal) if use_h else g

    # The counter breaks equal priorities first-in-first-out, so results are
    # deterministic and follow ACTIONS order (REQ-SRCH-02).
    tie = count()
    frontier = [(priority(start, 0), next(tie), start)]
    best_g = {start: 0}
    parent: dict[State, State | None] = {start: None}
    closed: set[State] = set()
    nodes_expanded = 0

    while frontier:
        _, _, state = heapq.heappop(frontier)
        if state in closed:
            continue  # stale duplicate left behind by a cheaper re-push
        # Goal test on pop, not on generation: required for UCS/A* optimality.
        # The goal node is not counted as expanded (its successors are never
        # generated), so start == goal gives 0 expansions (REQ-SRCH-13).
        if goal_test(state, goal):
            path = _reconstruct(parent, state)
            return path, path_cost(path), nodes_expanded
        closed.add(state)
        nodes_expanded += 1
        for nxt, _action, step in get_successors(state, grid):
            g = best_g[state] + step
            if nxt not in closed and g < best_g.get(nxt, g + 1):
                best_g[nxt] = g
                parent[nxt] = state
                heapq.heappush(frontier, (priority(nxt, g), next(tie), nxt))

    # Frontier exhausted: goal unreachable (REQ-SRCH-14).
    return None, None, nodes_expanded


def _reconstruct(parent: dict[State, State | None], state: State) -> list[State]:
    """Follow parent links back to the start.

    Args:
        parent: Child -> parent map built by search; the start maps to None.
        state: Goal state reached.

    Returns:
        States from start to ``state`` inclusive.
    """
    path = []
    node: State | None = state
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path
