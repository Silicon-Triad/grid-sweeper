"""CSP for cleaning-task scheduling (spec §6). Owner: Huzaifa.

Spec §6.2: "Variables: Each dirty location represents a CSP variable." /
"Domains: Each variable initially has the set of available time slots,
{T1,T2,...,Tn}, as its domain." / Precedence, latest-slot and slot-exclusivity
constraints.

Frozen interface: see docs/plan.md §4 and AGENTS.md.
"""


def select_unassigned_variable(assignment, domains, constraints):
    """Select an unassigned variable using MRV, ties broken by degree (spec §6.5).

    Spec: "Selects an unassigned variable using the Minimum Remaining Values
    (MRV), also called the most-constrained-variable heuristic. If multiple
    variables are tied, uses the degree heuristic to select the variable
    connected to the largest number of other unassigned variables through
    constraints."

    Args:
        assignment: Current variable assignments.
        domains: Current domains of the variables.
        constraints: Scheduling constraints.

    Returns:
        The next unassigned variable to select.
    """
    raise NotImplementedError


def order_domain_values(variable, assignment, domains, constraints):
    """Order candidate time slots using LCV (spec §6.5).

    Spec: "Orders the candidate time slots for the selected variable, using
    Least Constraining Value (LCV) heuristic to order values."

    Args:
        variable: Selected variable.
        assignment: Current partial assignment.
        domains: Current domains.
        constraints: Scheduling constraints.

    Returns:
        An ordered list of candidate time slots.
    """
    raise NotImplementedError


def is_consistent(variable, value, assignment, constraints):
    """Check precedence, latest-slot and slot-exclusivity (spec §6.5).

    Spec: "Checks precedence, latest-slot, and slot exclusivity constraints
    whenever the necessary assignments are available."

    Args:
        variable: Variable being assigned.
        value: Proposed time slot.
        assignment: Current partial assignment.
        constraints: Scheduling constraints.

    Returns:
        True if the proposed assignment does not violate any constraint that
        can be evaluated using the current assignment; otherwise, False.
    """
    raise NotImplementedError


def forward_check(variable, value, assignment, domains, constraints):
    """Prune infeasible values from related unassigned variables (spec §6.5).

    Spec: "Removes time-slot values that are no longer feasible for related
    unassigned variables. If any unassigned variable has an empty domain, the
    current assignment is rejected. Any domain values removed during forward
    checking must be restored when backtracking to a previous assignment."

    Args:
        variable: Newly assigned variable.
        value: Assigned time slot.
        assignment: Current assignment.
        domains: Current domains.
        constraints: Scheduling constraints.

    Returns:
        Updated domains if the assignment is consistent and no domain becomes
        empty; otherwise, a failure indication.
    """
    raise NotImplementedError


def backtracking_search(variables, domains, constraints):
    """Backtracking CSP solver (spec §6.5).

    Spec: "Implement a backtracking CSP solver using constraint checking,
    forward checking, and the required variable-selection heuristic." /
    "It must perform forward checking after assigning a value and backtrack
    when an assignment leads to failure."

    Args:
        variables: CSP variables.
        domains: Initial domains.
        constraints: Scheduling constraints.

    Returns:
        A complete assignment if a feasible schedule exists; otherwise, a
        failure indication.
    """
    raise NotImplementedError
