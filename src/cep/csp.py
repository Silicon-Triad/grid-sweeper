"""CSP for cleaning-task scheduling (spec §6). Owner: Huzaifa.

Spec §6.2: "Variables: Each dirty location represents a CSP variable." /
"Domains: Each variable initially has the set of available time slots,
{T1,T2,...,Tn}, as its domain." / Precedence, latest-slot and slot-exclusivity
constraints.

Frozen interface: see docs/plan.md §4 and AGENTS.md.

Types (DEC-06): variables are task labels ``"D1"…"Dn"``; slots are ints
``1…n`` (shown as ``T<n>`` only in output); ``domains`` is
``dict[label, list[int]]`` in ascending order; ``assignment`` is
``dict[label, int]``; ``constraints`` is ``env.Constraints``.
"""

from cep.env import Constraints, Label, Slot

Domains = dict[Label, list[Slot]]
Assignment = dict[Label, Slot]


def _pair_ok(
    x: Label, x_slot: Slot, y: Label, y_slot: Slot, constraints: Constraints
) -> bool:
    """Check the binary constraints between two different tasks.

    Slot exclusivity (REQ-CSP-07) and precedence in either direction
    (REQ-CSP-05) are the only constraints that involve two tasks; latest-slot
    is unary and checked separately. Shared by ``is_consistent``,
    ``forward_check`` and ``order_domain_values`` so all three agree on what
    "conflict" means.

    Args:
        x: First task.
        x_slot: Slot proposed for ``x``.
        y: Second task (different from ``x``).
        y_slot: Slot proposed for ``y``.
        constraints: Scheduling constraints.

    Returns:
        True if the two placements do not violate any binary constraint.
    """
    if x_slot == y_slot:
        return False
    for before, after in constraints.precedence:
        if (before, after) == (x, y) and not x_slot < y_slot:
            return False
        if (before, after) == (y, x) and not y_slot < x_slot:
            return False
    return True


def _latest_ok(variable: Label, value: Slot, constraints: Constraints) -> bool:
    """Check the latest-slot constraint of one task (REQ-CSP-06).

    Args:
        variable: Task.
        value: Proposed slot.
        constraints: Scheduling constraints.

    Returns:
        True if ``variable`` has no latest-slot limit or ``value`` is within it.
    """
    limit = constraints.latest.get(variable)
    return limit is None or value <= limit


def _degree(variable: Label, assignment: Assignment, constraints: Constraints) -> int:
    """Count distinct other unassigned tasks linked by precedence (DEC-05).

    Slot exclusivity is not counted: it links every pair of tasks, so it adds
    the same amount to every score and could never change the ranking (#40).

    Args:
        variable: Task whose degree is wanted.
        assignment: Current partial assignment.
        constraints: Scheduling constraints.

    Returns:
        Number of distinct neighbours that are still unassigned.
    """
    neighbours = set()
    for before, after in constraints.precedence:
        if before == variable:
            neighbours.add(after)
        elif after == variable:
            neighbours.add(before)
    # A self-precedence (X,X) names X itself, which is not an "other" variable.
    neighbours.discard(variable)
    return sum(1 for n in neighbours if n not in assignment)


def select_unassigned_variable(assignment, domains, constraints):
    """Select an unassigned variable using MRV, ties broken by degree (spec §6.5).

    Spec: "Selects an unassigned variable using the Minimum Remaining Values
    (MRV), also called the most-constrained-variable heuristic. If multiple
    variables are tied, uses the degree heuristic to select the variable
    connected to the largest number of other unassigned variables through
    constraints."

    Order of tie-breaks (REQ-CSP-13, DEC-05): fewest remaining values, then
    highest degree (precedence links to other unassigned tasks only), then
    file order D1…Dn.

    Args:
        assignment: Current variable assignments.
        domains: Current domains of the variables.
        constraints: Scheduling constraints.

    Returns:
        The next unassigned variable to select, or None if every variable is
        already assigned.
    """
    unassigned = [v for v in constraints.variables if v not in assignment]
    if not unassigned:
        return None
    # min() keeps the first of equal keys, and the list is in file order, so
    # the last tie-break (D1…Dn, DEC-05) needs no extra key.
    return min(
        unassigned,
        key=lambda v: (len(domains[v]), -_degree(v, assignment, constraints)),
    )


def order_domain_values(variable, assignment, domains, constraints):
    """Order candidate time slots using LCV (spec §6.5).

    Spec: "Orders the candidate time slots for the selected variable, using
    Least Constraining Value (LCV) heuristic to order values."

    For each slot, counts how many values it would rule out of the domains of
    the other unassigned tasks (same slot, or wrong side of a precedence).
    Fewest ruled out comes first. Equal counts keep the domain's ascending
    order (DEC-06), because ``sorted`` is stable.

    Args:
        variable: Selected variable.
        assignment: Current partial assignment.
        domains: Current domains.
        constraints: Scheduling constraints.

    Returns:
        An ordered list of candidate time slots (every value in
        ``domains[variable]``; consistency is checked by the caller).
    """
    others = [v for v in constraints.variables if v != variable and v not in assignment]

    def ruled_out(value: Slot) -> int:
        return sum(
            1
            for other in others
            for other_value in domains[other]
            if not _pair_ok(variable, value, other, other_value, constraints)
        )

    return sorted(domains[variable], key=ruled_out)


def is_consistent(variable, value, assignment, constraints):
    """Check precedence, latest-slot and slot-exclusivity (spec §6.5).

    Spec: "Checks precedence, latest-slot, and slot exclusivity constraints
    whenever the necessary assignments are available."

    Only constraints whose tasks are all assigned (counting ``variable`` =
    ``value``) are checked; the rest are left for later (REQ-CSP-15).

    Args:
        variable: Variable being assigned.
        value: Proposed time slot.
        assignment: Current partial assignment.
        constraints: Scheduling constraints.

    Returns:
        True if the proposed assignment does not violate any constraint that
        can be evaluated using the current assignment; otherwise, False.
    """
    if not _latest_ok(variable, value, constraints):  # REQ-CSP-06
        return False
    # (X,X) can never hold: no slot comes strictly before itself (DEC-12).
    if (variable, variable) in constraints.precedence:
        return False
    # Exclusivity and precedence against every task already placed
    # (REQ-CSP-05, REQ-CSP-07). Skipping ``variable`` lets callers pass an
    # assignment that already contains it.
    return all(
        _pair_ok(variable, value, other, slot, constraints)
        for other, slot in assignment.items()
        if other != variable
    )


def forward_check(variable, value, assignment, domains, constraints):
    """Prune infeasible values from related unassigned variables (spec §6.5).

    Spec: "Removes time-slot values that are no longer feasible for related
    unassigned variables. If any unassigned variable has an empty domain, the
    current assignment is rejected. Any domain values removed during forward
    checking must be restored when backtracking to a previous assignment."

    The input ``domains`` is never modified: pruning happens on a copy that is
    returned. Backtracking restores the removed values simply by going on with
    the ``domains`` it had before the call (REQ-CSP-17).

    Args:
        variable: Newly assigned variable.
        value: Assigned time slot.
        assignment: Current assignment.
        domains: Current domains.
        constraints: Scheduling constraints.

    Returns:
        Updated domains if the assignment is consistent and no domain becomes
        empty; otherwise, None (REQ-CSP-16).
    """
    new_domains = {v: list(values) for v, values in domains.items()}
    new_domains[variable] = [value]
    for other in constraints.variables:
        if other == variable or other in assignment:
            continue
        new_domains[other] = [
            v
            for v in new_domains[other]
            if _pair_ok(variable, value, other, v, constraints)
        ]
        if not new_domains[other]:
            return None
    return new_domains


def backtracking_search(variables, domains, constraints):
    """Backtracking CSP solver (spec §6.5).

    Spec: "Implement a backtracking CSP solver using constraint checking,
    forward checking, and the required variable-selection heuristic." /
    "It must perform forward checking after assigning a value and backtrack
    when an assignment leads to failure."

    Before searching, values above a task's latest slot are removed (they can
    never be consistent), so MRV sees those tasks as more constrained from the
    start. Each step: pick a variable (MRV/degree), try its values in LCV
    order, keep a value only if it is consistent and forward checking leaves
    no empty domain; otherwise undo and try the next value (REQ-CSP-18).

    Args:
        variables: CSP variables; must be the same tasks as
            ``constraints.variables`` (every dirty cell, REQ-CSP-03).
        domains: Initial domains (not modified).
        constraints: Scheduling constraints.

    Returns:
        A complete assignment (label -> slot) if a feasible schedule exists;
        otherwise, None (REQ-CSP-11, REQ-CSP-12).

    Raises:
        ValueError: If ``variables`` and ``constraints.variables`` differ.
    """
    assignment, _ = backtracking_search_with_stats(variables, domains, constraints)
    return assignment


def new_stats() -> dict[str, int]:
    """Return zeroed search counters for ``backtracking_search_with_stats``.

    Returns:
        ``assignments_tried``: values that passed ``is_consistent`` and were
        assigned; ``fc_rejections``: of those, how many forward checking
        rejected at once (an empty domain); ``backtracks``: assignments
        undone because every deeper branch failed (a dead end found only
        after recursing); ``values_pruned``: domain values removed by
        successful forward checks; ``values_restored``: of those, how many
        came back because their branch was abandoned (REQ-CSP-17).
    """
    return {
        "assignments_tried": 0,
        "fc_rejections": 0,
        "backtracks": 0,
        "values_pruned": 0,
        "values_restored": 0,
    }


def backtracking_search_with_stats(
    variables: list[Label], domains: Domains, constraints: Constraints
) -> tuple[Assignment | None, dict[str, int]]:
    """Run ``backtracking_search`` and also return its search counters.

    Same solver, same result: ``backtracking_search`` calls this function
    and drops the counters (DEC-16). Added so the notebook can show
    backtracking and domain restoration actually happening.

    Args:
        variables: CSP variables; must equal ``constraints.variables``.
        domains: Initial domains (not modified).
        constraints: Scheduling constraints.

    Returns:
        ``(assignment or None, stats)``; see ``new_stats`` for the keys.

    Raises:
        ValueError: If ``variables`` and ``constraints.variables`` differ.
    """
    if set(variables) != set(constraints.variables):
        raise ValueError("variables must match constraints.variables")

    stats = new_stats()
    start = {
        v: [s for s in domains[v] if _latest_ok(v, s, constraints)] for v in variables
    }
    if any(not values for values in start.values()):
        return None, stats
    return _backtrack({}, start, constraints, stats), stats


def _backtrack(
    assignment: Assignment,
    domains: Domains,
    constraints: Constraints,
    stats: dict[str, int],
) -> Assignment | None:
    """Recursive step of ``backtracking_search``.

    Args:
        assignment: Partial assignment, extended in place and undone on failure.
        domains: Domains after forward checking for ``assignment``.
        constraints: Scheduling constraints.
        stats: Counters updated in place (see ``new_stats``).

    Returns:
        A complete assignment, or None if this branch has no solution.
    """
    variable = select_unassigned_variable(assignment, domains, constraints)
    if variable is None:
        return dict(assignment)
    for value in order_domain_values(variable, assignment, domains, constraints):
        if not is_consistent(variable, value, assignment, constraints):
            continue
        assignment[variable] = value
        stats["assignments_tried"] += 1
        pruned = forward_check(variable, value, assignment, domains, constraints)
        if pruned is None:
            stats["fc_rejections"] += 1
        else:
            # Values removed from the other tasks' domains by this check
            # (``variable`` itself shrinking to [value] is not pruning).
            removed = sum(
                len(domains[v]) - len(pruned[v]) for v in domains if v != variable
            )
            stats["values_pruned"] += removed
            result = _backtrack(assignment, pruned, constraints, stats)
            if result is not None:
                return result
            stats["backtracks"] += 1
            stats["values_restored"] += removed
        # Backtrack: drop the value. ``domains`` was never changed, so the
        # values forward checking removed are back for the next try.
        del assignment[variable]
    return None
