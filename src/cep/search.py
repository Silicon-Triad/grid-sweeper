"""Graph-based search for robot navigation (spec §5). Owner: Mujtaba.

Spec §5.3: "State: Represent the robot's position as (row,column)." /
"Actions: UP, DOWN, LEFT, and RIGHT. An action is valid only if the resulting
cell is within the grid boundaries and is not an obstacle." / "Step cost: Each
valid movement has a cost of 1."

Frozen interface: see docs/plan.md §4 and AGENTS.md.
"""


def get_successors(state, grid):
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
    raise NotImplementedError


def goal_test(state, goal_state):
    """Check whether the goal has been reached (spec §5.5).

    Args:
        state: Current robot position.
        goal_state: Target position.

    Returns:
        True if state equals goal_state; otherwise, False.
    """
    raise NotImplementedError


def path_cost(path):
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
    raise NotImplementedError


def heuristic(state, goal_state):
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
    raise NotImplementedError


def search(grid, start, goal, algorithm):
    """Implement the selected search algorithm (spec §5.5).

    Spec §5.4: "The start and goal positions must be provided as inputs rather
    than hardcoded in the search algorithm." / "The program must correctly
    handle cases where the start equals the goal or no path exists."

    Args:
        grid: Environment representation.
        start: Starting position.
        goal: Target position.
        algorithm: Selected graph-search algorithm.

    Returns:
        path: Sequence of states from start to goal, or an appropriate
            indication that no path exists.
        cost: Total path cost, if a path is found.
        nodes_expanded: Number of nodes expanded during the search.
    """
    raise NotImplementedError
