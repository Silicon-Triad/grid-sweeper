"""Generate reproducible environment and scheduling input files."""

from __future__ import annotations

import argparse
import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cep.env import parse_environment, parse_schedule  # noqa: E402


def neighbours(cell, rows, cols):
    """Return valid four-direction neighbouring cells."""
    r, c = cell
    return [
        (nr, nc)
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
        if 0 <= nr < rows and 0 <= nc < cols
    ]


def all_reachable(rows, cols, obstacles, charger, dirty):
    """Check whether all dirty cells are reachable from the charger."""
    visited = {charger}
    queue = deque([charger])

    while queue:
        current = queue.popleft()
        for cell in neighbours(current, rows, cols):
            if cell not in obstacles and cell not in visited:
                visited.add(cell)
                queue.append(cell)

    return all(cell in visited for cell in dirty)


def make_environment(rng, rows, cols, obstacle_count, dirt_count, unreachable):
    """Generate a valid environment file."""
    if rows <= 0 or cols <= 0:
        raise ValueError("Grid dimensions must be positive.")
    if dirt_count < 1:
        raise ValueError("Dirty-cell count must be at least 1.")
    if obstacle_count < 0:
        raise ValueError("Obstacle count cannot be negative.")
    if obstacle_count + dirt_count + 1 > rows * cols:
        raise ValueError("Not enough cells for obstacles, dirt, and charger.")

    cells = [(r, c) for r in range(rows) for c in range(cols)]

    if unreachable:
        if rows < 2 or cols < 2:
            raise ValueError("Unreachable mode requires at least a 2x2 grid.")

        charger = (0, 0)
        target = (rows - 1, cols - 1)
        blocked = set(neighbours(target, rows, cols))

        if obstacle_count < len(blocked):
            raise ValueError(
                f"Unreachable mode requires at least {len(blocked)} obstacles."
            )

        available = [
            cell
            for cell in cells
            if cell not in blocked and cell not in {charger, target}
        ]
        other_dirt = rng.sample(available, dirt_count - 1)
        dirty = [target, *other_dirt]

        remaining = [cell for cell in available if cell not in other_dirt]
        extra = rng.sample(remaining, obstacle_count - len(blocked))
        obstacles = blocked | set(extra)

    else:
        for _ in range(1000):
            charger = rng.choice(cells)
            available = [cell for cell in cells if cell != charger]
            dirty = rng.sample(available, dirt_count)
            remaining = [cell for cell in available if cell not in dirty]
            obstacles = set(rng.sample(remaining, obstacle_count))

            if all_reachable(rows, cols, obstacles, charger, dirty):
                break
        else:
            raise ValueError(
                "Could not generate a reachable grid. Try fewer obstacles "
                "or a larger grid."
            )

    return (
        "\n".join(
            [
                f"{rows},{cols}",
                str(len(obstacles)),
                ", ".join(map(str, sorted(obstacles))),
                str(len(dirty)),
                ", ".join(map(str, dirty)),
                str(charger),
            ]
        )
        + "\n"
    )


def make_schedule(rng, dirt_count, infeasible):
    """Generate a feasible or deliberately infeasible schedule."""
    if dirt_count < 1:
        raise ValueError("At least one dirty cell is required.")

    tasks = [f"D{i}" for i in range(1, dirt_count + 1)]
    order = tasks[:]
    rng.shuffle(order)

    if infeasible:
        if dirt_count >= 2:
            precedence = [(order[0], order[1]), (order[1], order[0])]
        else:
            precedence = [(order[0], order[0])]
        latest = []
    else:
        precedence = [
            (order[i], order[j])
            for i in range(dirt_count)
            for j in range(i + 1, dirt_count)
            if rng.random() < 0.3
        ]
        latest = [
            (task, f"T{index + 1}")
            for index, task in enumerate(order)
            if rng.random() < 0.3
        ]

    lines = [
        str(dirt_count),
        str(len(precedence)),
        *[f"({before},{after})" for before, after in precedence],
        str(len(latest)),
        *[f"({task},{slot})" for task, slot in latest],
    ]
    return "\n".join(lines) + "\n"


def main():
    """Read options, generate files, and validate their formats."""
    parser = argparse.ArgumentParser(
        description="Generate Grid Sweeper environment and schedule files."
    )
    parser.add_argument(
        "--size", nargs=2, type=int, metavar=("ROWS", "COLS"), default=(8, 8)
    )
    parser.add_argument("--rows", type=int)
    parser.add_argument("--cols", type=int)
    parser.add_argument("--obstacles", type=int, default=6)
    parser.add_argument("--dirt", type=int, default=4)
    parser.add_argument(
        "--mode",
        choices=("reachable", "unreachable", "feasible", "infeasible"),
        default="reachable",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("generated"))
    args = parser.parse_args()

    rows = args.rows if args.rows is not None else args.size[0]
    cols = args.cols if args.cols is not None else args.size[1]
    rng = random.Random(args.seed)

    environment = make_environment(
        rng,
        rows,
        cols,
        args.obstacles,
        args.dirt,
        args.mode == "unreachable",
    )
    schedule = make_schedule(rng, args.dirt, args.mode == "infeasible")

    grid = parse_environment(environment, source="generated Environment.txt")
    parse_schedule(schedule, grid, source="generated Schedule.txt")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    env_path = args.output_dir / "Environment.txt"
    schedule_path = args.output_dir / "Schedule.txt"

    env_path.write_text(environment, encoding="utf-8")
    schedule_path.write_text(schedule, encoding="utf-8")

    print(f"Mode: {args.mode}")
    print(f"Seed: {args.seed}")
    print(f"Environment: {env_path}")
    print(f"Schedule: {schedule_path}")
    print("Both files passed input-format validation.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
