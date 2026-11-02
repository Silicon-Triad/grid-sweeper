"""Assemble notebook/CS24045.ipynb from src/cep/ and markdown cells (issue #27).

Stub created by the scaffold (#1). Usage:

    python tools/build_notebook.py           # build the notebook
    python tools/build_notebook.py --check   # fail if committed != rebuilt
"""

import argparse
import sys
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parent.parent / "notebook" / "CS24045.ipynb"


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed notebook equals a fresh build",
    )
    args = parser.parse_args(argv)

    if args.check and not NOTEBOOK.exists():
        print(f"SKIP: {NOTEBOOK.name} not present yet")
        return 0
    print("build_notebook.py is not implemented yet (issue #27)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
