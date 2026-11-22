"""Integration of CSP scheduling and graph-based search (spec §7).

Owner: Muhammad Ahmed Qazi.

Frozen interface: see docs/plan.md §4 and AGENTS.md.

``execute_schedule`` is the frozen function. ``run_integration`` does the same
work but also keeps per-leg details (path, cost, nodes expanded) and a failure
reason, which the display (#24) needs; the frozen return value has no room for
them. ``plan_and_execute`` runs the whole pipeline: CSP first, then search.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from cep.csp import backtracking_search
from cep.env import Constraints, Grid, Label, Slot, State, initial_domains
from cep.search import path_cost, search

# Name used for the charging station in leg descriptions and messages.
CHARGER = "C"


@dataclass(frozen=True)
class Leg:
    """One search call between two consecutive stops (spec §7.2 step 3/6).

    Attributes:
        source: Label of the start stop (``"C"`` for the charger).
        target: Label of the goal stop.
        start: Start cell.
        goal: Goal cell.
        path: States from start to goal, or None if no path exists.
        cost: Path cost, or None if no path exists.
        nodes_expanded: Nodes expanded by this search call.
    """

    source: str
    target: str
    start: State
    goal: State
    path: list[State] | None
    cost: int | None
    nodes_expanded: int


@dataclass(frozen=True)
class IntegrationResult:
    """Everything the integrated run produced (spec §7.2 step 8, REQ-INT-08).

    Attributes:
        algorithm: Search algorithm used.
        schedule: Labels in slot order (empty if the CSP failed).
        assignment: CSP assignment label -> slot, or None if the CSP failed or
            the schedule was given directly.
        legs: Search calls made, in order; the last one failed if
            ``success`` is False because of a missing path.
        cleaned: Labels cleaned, in visit order.
        complete_path: Joined path; on failure, the part walked so far
            (DEC-15).
        total_cost: Cost of ``complete_path``.
        success: True only if every task was cleaned and the robot is back at
            the charger (REQ-INT-07).
        reason: Empty on success; otherwise why the run failed.
    """

    algorithm: str
    schedule: list[Label]
    assignment: dict[Label, Slot] | None
    legs: list[Leg]
    cleaned: list[Label]
    complete_path: list[State]
    total_cost: int
    success: bool
    reason: str


def schedule_from_assignment(assignment: Mapping[Label, Slot]) -> list[Label]:
    """Order tasks by their assigned slot (spec §7.1 step 2, REQ-INT-01).

    Slots are ints, so sorting by value is numeric: T10 comes after T9
    (DEC-06).

    Args:
        assignment: CSP assignment label -> slot.

    Returns:
        Labels in slot order.
    """
    return sorted(assignment, key=lambda label: assignment[label])


def run_integration(
    grid: Grid,
    charging_station: State,
    schedule: Sequence[Label],
    algorithm: str,
) -> IntegrationResult:
    """Execute a schedule and keep per-leg details (spec §7.2 procedure).

    Args:
        grid: Environment loaded from Environment.txt.
        charging_station: Start and end cell of the journey.
        schedule: Task labels in slot order; converted to cells via
            ``grid.dirty``.
        algorithm: Search algorithm name, one of ``ALGORITHMS``.

    Returns:
        The full result; see ``IntegrationResult``.

    Raises:
        KeyError: If a label is not a dirty cell of ``grid``.
        ValueError: If ``algorithm`` is unknown (raised by ``search``).
    """
    # Stops: each scheduled task, then back to the charger (steps 2 and 6).
    stops = [(label, grid.dirty[label]) for label in schedule]
    stops.append((CHARGER, charging_station))

    current_label, current = CHARGER, charging_station  # step 1
    complete_path = [charging_station]
    legs: list[Leg] = []
    cleaned: list[Label] = []

    for label, cell in stops:
        path, cost, nodes = search(grid, current, cell, algorithm)  # step 3
        legs.append(Leg(current_label, label, current, cell, path, cost, nodes))
        if path is None:
            # Step 9: stop and never claim success. The path walked so far is
            # kept so the display can show where the robot got stuck (DEC-15).
            reason = (
                f"no path from {current_label} {current} to {label} {cell}"
                f" ({algorithm})"
            )
            return IntegrationResult(
                algorithm,
                list(schedule),
                None,
                legs,
                cleaned,
                complete_path,
                path_cost(complete_path),
                False,
                reason,
            )
        # Step 4: path[0] equals the last state already in complete_path.
        complete_path.extend(path[1:])
        if label != CHARGER:
            cleaned.append(label)  # step 5: reached, so cleaned (REQ-INT-03)
        current_label, current = label, cell

    return IntegrationResult(
        algorithm,
        list(schedule),
        None,
        legs,
        cleaned,
        complete_path,
        path_cost(complete_path),  # step 7
        True,
        "",
    )


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
    result = run_integration(grid, charging_station, schedule, algorithm)
    return result.complete_path, result.total_cost, result.success


def plan_and_execute(
    grid: Grid, constraints: Constraints, algorithm: str
) -> IntegrationResult:
    """Run the CSP solver, then execute its schedule (spec §7.1, REQ-INT-09).

    Args:
        grid: Environment loaded from Environment.txt.
        constraints: Scheduling problem loaded from Schedule.txt.
        algorithm: Search algorithm name.

    Returns:
        The integration result. If the CSP finds no schedule, no search is
        run and the result reports failure with the robot still at the
        charger (spec §7.1 item 6).
    """
    assignment = backtracking_search(
        list(constraints.variables), initial_domains(constraints), constraints
    )
    if assignment is None:
        return IntegrationResult(
            algorithm,
            [],
            None,
            [],
            [],
            [grid.charger],
            0,
            False,
            "CSP solver found no feasible schedule",
        )
    schedule = schedule_from_assignment(assignment)
    result = run_integration(grid, grid.charger, schedule, algorithm)
    # The dataclass is frozen, so replace() makes a copy with the assignment.
    return replace(result, assignment=assignment)
