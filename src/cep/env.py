"""Environment and schedule loading, grid representation, validation. Owner: Ashar.

Spec §5.2 (Environment Input File):
    "Use the following format, with one item or group of items per line:
    1. Grid dimensions as rows,columns.
    2. Number of obstacles.
    3. Coordinates of all obstacles, represented as (row,column) tuples.
    4. Number of dirty locations.
    5. Coordinates of all dirty locations, represented as (row,column) tuples.
    6. Coordinate of the charging station, represented as a (row,column) tuple.
    Coordinates are zero-based. The first dirty location listed is D1, the
    second is D2, and so on."

Spec §6.3 (Scheduling Input File):
    "1. Number of available time slots.
    2. Number of precedence constraints.
    3. One pair (task_before,task_after) per line for each precedence constraint.
    4. Number of latest-slot constraints.
    5. One pair (task,latest_slot) per line for each latest-slot constraint.
    Slot exclusivity applies automatically to all tasks and does not need to be
    listed in the file."

Spec §6.4:
    "The number of available time slots must be at least the number of dirty
    locations." / "Task labels used in the scheduling constraints must
    correspond to the dirty locations defined by Environment.txt."

Internal types (``state``, ``Grid``, ``Constraints``, algorithm names) are
fixed in issue #3 and documented here and in AGENTS.md. No implementation in
the scaffold.
"""
