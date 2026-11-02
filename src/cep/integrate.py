"""Integration of CSP scheduling and graph-based search (spec §7). Owner: Qazi.

Frozen interface: see docs/plan.md §4 and AGENTS.md.
"""


def execute_schedule(grid, charging_station, schedule, algorithm):
    """Execute the CSP-generated schedule using graph-based search (spec §7.2).

    Spec procedure (abridged): start at the charging station; for each
    cleaning location in schedule order "call search using the robot's current
    position as the start state and the next cleaning location as the goal
    state"; "Append each returned path to complete_path, avoiding duplication
    of shared endpoints"; finally search back to the charging station. "If a
    required path cannot be found, the program must report failure rather
    than claim that the cleaning task was completed successfully."

    Args:
        grid: Environment loaded from Environment.txt.
        charging_station: Position of the charging station.
        schedule: Cleaning tasks ordered according to their assigned time
            slots by the CSP solver.
        algorithm: Graph-search algorithm to use for navigation.

    Returns:
        complete_path: Combined path followed by the robot, from the charging
            station through all scheduled cleaning locations and back to the
            charging station.
        total_cost: Total navigation cost of the complete journey.
        success: Indicates whether all dirty locations were cleaned and the
            robot returned to the charging station successfully.
    """
    raise NotImplementedError
