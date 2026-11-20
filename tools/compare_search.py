"""Write the UCS vs A* comparison table + plots (issue #16, REQ-CMP-02).

Usage:

    python tools/compare_search.py [ENV_FILE] [--out report/figures]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from cep.compare import (  # noqa: E402
    SCENARIOS,
    charger_pairs,
    compare_pairs,
    format_table,
    scaling,
)
from cep.env import ALGORITHMS, load_environment  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("env", nargs="?", default=ROOT / "data" / "Environment.txt")
    parser.add_argument("--out", default=ROOT / "report" / "figures", type=Path)
    parser.add_argument("--sizes", default="5,10,20,40,80", help="grid sides")
    args = parser.parse_args(argv)

    grid = load_environment(args.env)
    pair_runs = compare_pairs(grid, charger_pairs(grid), repeats=5)
    sizes = [int(s) for s in args.sizes.split(",")]
    scale = {sc: scaling(sizes, scenario=sc) for sc in SCENARIOS}

    args.out.mkdir(parents=True, exist_ok=True)
    table = (
        f"## Start/goal pairs ({Path(args.env).name})\n\n{format_table(pair_runs)}\n\n"
        + "".join(
            f"## Scaling: open grids, {sc}\n\n{format_table(runs)}\n\n"
            for sc, runs in scale.items()
        )
    )
    (args.out / "search_comparison.md").write_text(table)
    print(table)

    import matplotlib

    matplotlib.use("Agg")  # headless: CI and the container have no display
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    labels = list(dict.fromkeys(r.label for r in pair_runs))
    width = 0.8 / len(ALGORITHMS)
    for i, alg in enumerate(ALGORITHMS):
        nodes = [r.nodes_expanded for r in pair_runs if r.algorithm == alg]
        xs = [x + i * width for x in range(len(labels))]
        axes[0].bar(xs, nodes, width, label=alg)
        for sc, runs in scale.items():
            ys = [r.nodes_expanded for r in runs if r.algorithm == alg]
            axes[1].plot(sizes, ys, marker="o", label=f"{alg} ({sc})")
    axes[0].set_xticks([x + width / 2 for x in range(len(labels))], labels)
    axes[0].set_title("Nodes expanded per start/goal pair")
    axes[0].set_ylabel("nodes expanded")
    axes[1].set_title("Scaling on open n x n grids")
    axes[1].set_xlabel("grid side n")
    axes[1].set_ylabel("nodes expanded")
    for ax in axes:
        ax.legend()
    fig.tight_layout()
    fig.savefig(args.out / "search_comparison.png", dpi=150)
    print(f"wrote {args.out / 'search_comparison.png'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
