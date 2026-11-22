"""Assemble notebook/CS24045.ipynb from src/cep/ and markdown cells (issue #27).

The submitted notebook must run on its own with only the input files next to
it (spec §8.1, §10), so the code of every ``src/cep`` module is copied into a
cell and the ``from cep... import`` lines are dropped: in the notebook all
names live in one namespace. Markdown comes from ``notebook/markdown/``.
Outputs are never stored (nbstripout); cell ids are fixed so a rebuild is
byte-identical. Usage:

    python tools/build_notebook.py           # build the notebook
    python tools/build_notebook.py --check   # fail if committed != rebuilt
"""

import argparse
import base64
import re
import subprocess
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebook" / "CS24045.ipynb"
MARKDOWN = ROOT / "notebook" / "markdown"
SRC = ROOT / "src" / "cep"
SCREENSHOTS = ROOT / "report" / "screenshots"

# ``![alt](attachment:name.png)`` in a markdown cell embeds report/screenshots/name.png.
# Attachments live inside the .ipynb, so the images survive uploading the
# notebook alone to Classroom (spec §10.1), unlike links to files beside it.
_ATTACHMENT = re.compile(r"\(attachment:([\w.-]+\.png)\)")

# Imports between our own modules; dropped because the cells share a namespace.
_CEP_IMPORT = re.compile(r"^(from cep(\.\w+)? import .*|import cep.*)\n", re.MULTILINE)

CONFIG = '''\
from pathlib import Path

# Input files (spec §8.1): change these names to run other files.
ENV_FILE = "Environment.txt"
SCHEDULE_FILE = "Schedule.txt"
SAMPLE_ENV_FILE = "Environment_Sample.txt"
SAMPLE_SCHEDULE_FILE = "Schedule_Sample.txt"
ERROR_ENV_FILE = "Environment_Error.txt"
ERROR_SCHEDULE_FILE = "Schedule_Error.txt"

# Notebook folder first (submission), then the repository layout.
SEARCH_DIRS = [Path.cwd(), Path.cwd() / "data", Path.cwd().parent / "data"]


def find_file(name):
    """Return the first existing ``name`` in SEARCH_DIRS.

    Args:
        name: File name.

    Returns:
        Path to the file.

    Raises:
        FileNotFoundError: If no folder has it.
    """
    for folder in SEARCH_DIRS:
        if (folder / name).is_file():
            return folder / name
    raise FileNotFoundError(f"{name} not found in {[str(d) for d in SEARCH_DIRS]}")
'''

ENV_RUN = """\
grid = load_environment(find_file(ENV_FILE))
constraints = load_schedule(find_file(SCHEDULE_FILE), grid)
print(f"Grid {grid.rows}x{grid.cols}, {len(grid.obstacles)} obstacles, "
      f"charger {grid.charger}")
print("Dirty cells:", dict(grid.dirty))
print(f"Slots: {constraints.num_slots}, precedence: {list(constraints.precedence)}, "
      f"latest: {dict(constraints.latest)}")
print()
print(format_grid(grid))
print(LEGEND)
"""

SEARCH_DEMO = """\
# Each algorithm from the charger to the first dirty cell, plus the edge cases.
first = next(iter(grid.dirty))
for algorithm in ALGORITHMS:
    path, cost, nodes = search(grid, grid.charger, grid.dirty[first], algorithm)
    print(f"{algorithm}: C -> {first}: cost {cost}, nodes expanded {nodes}")
    print("  path:", path)
print("start == goal:", search(grid, grid.charger, grid.charger, "astar"))
print("path_cost([]) =", path_cost([]))
"""

COMPARE = """\
import matplotlib.pyplot as plt

pair_runs = compare_pairs(grid, charger_pairs(grid), repeats=3)
print(format_table(pair_runs, tablefmt="grid"))

sizes = [5, 10, 20, 40]
scale = {sc: scaling(sizes, repeats=1, scenario=sc) for sc in SCENARIOS}
for sc, runs in scale.items():
    print(f"\\nScaling, open grids, {sc}:")
    print(format_table(runs, tablefmt="grid"))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
labels = list(dict.fromkeys(r.label for r in pair_runs))
width = 0.8 / len(ALGORITHMS)
for i, alg in enumerate(ALGORITHMS):
    nodes = [r.nodes_expanded for r in pair_runs if r.algorithm == alg]
    axes[0].bar([x + i * width for x in range(len(labels))], nodes, width, label=alg)
    for sc, runs in scale.items():
        ys = [r.nodes_expanded for r in runs if r.algorithm == alg]
        axes[1].plot(sizes, ys, marker="o", label=f"{alg} ({sc})")
axes[0].set_xticks([x + width / 2 for x in range(len(labels))], labels)
axes[0].set_title("Nodes expanded per start/goal pair")
axes[1].set_title("Scaling on open n x n grids")
axes[1].set_xlabel("grid side n")
for ax in axes:
    ax.set_ylabel("nodes expanded")
    ax.legend()
fig.tight_layout()
plt.show()
"""

CSP_RUN = """\
assignment = backtracking_search(
    list(constraints.variables), initial_domains(constraints), constraints
)
print(format_schedule_proof(assignment, constraints))
"""

INTEGRATION_RUN = """\
for algorithm in ALGORITHMS:
    print(format_result(plan_and_execute(grid, constraints, algorithm), grid))
    print()
"""

RUN_CASE = '''\
def run_case(env_name, schedule_name):
    """One test run: configuration, schedule proof, integration per algorithm.

    Input errors are reported, not raised, so a bad file never stops the
    notebook (spec §8.2 failure case).

    Args:
        env_name: Environment file name.
        schedule_name: Schedule file name.
    """
    print(f"Configuration: {env_name} + {schedule_name}")
    try:
        g = load_environment(find_file(env_name))
        c = load_schedule(find_file(schedule_name), g)
    except (InputError, OSError) as err:
        print(f"FAILURE detected while loading input: {err}")
        return
    print(format_grid(g))
    print(LEGEND)
    print()
    a = backtracking_search(list(c.variables), initial_domains(c), c)
    print(format_schedule_proof(a, c))
    for algorithm in ALGORITHMS:
        print()
        print(format_result(plan_and_execute(g, c, algorithm), g))
'''


def md(name: str) -> str:
    """Read a markdown cell file, dropping HTML comment lines meant for editors.

    Args:
        name: File name in ``notebook/markdown``.

    Returns:
        Cell text.
    """
    text = (MARKDOWN / name).read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if not ln.startswith("<!-- Notebook")]
    return "\n".join(lines).strip()


def src(module: str) -> str:
    """Return a module's source without imports of other ``cep`` modules.

    Args:
        module: Module name in ``src/cep``.

    Returns:
        Cell code.
    """
    text = (SRC / f"{module}.py").read_text(encoding="utf-8")
    text = _CEP_IMPORT.sub("", text)
    # Removing a whole import group leaves an extra blank line behind.
    return re.sub(r"\n{4,}", "\n\n\n", text).strip()


def cells() -> list[tuple[str, str]]:
    """Notebook layout in order: ``(kind, text)`` with kind ``md`` or ``code``.

    Returns:
        Cells in notebook order.
    """
    return [
        ("md", md("00_header.md")),  # spec §8.1: names + roll numbers first
        ("md", md("01_config.md")),
        ("code", CONFIG),
        ("md", md("02_env.md")),
        ("code", src("env")),
        ("md", md("02b_render.md")),
        ("code", src("render")),
        ("md", md("03_env_run.md")),
        ("code", ENV_RUN),
        ("md", md("04_search.md")),
        ("code", src("search")),
        ("code", SEARCH_DEMO),
        ("md", md("heuristic.md")),
        ("md", md("05_compare_code.md")),
        ("code", src("compare")),
        ("md", md("06_compare.md")),
        ("code", COMPARE),
        ("md", md("07_csp.md")),
        ("code", src("csp")),
        ("code", CSP_RUN),
        ("md", md("08_integration.md")),
        ("code", src("integrate")),
        ("code", INTEGRATION_RUN),
        ("md", md("09_testing.md")),
        ("code", RUN_CASE),
        ("md", md("10_run1.md")),
        ("code", "run_case(ENV_FILE, SCHEDULE_FILE)"),
        ("md", md("11_run1_shot.md")),
        ("md", md("12_run2.md")),
        ("code", "run_case(SAMPLE_ENV_FILE, SAMPLE_SCHEDULE_FILE)"),
        ("md", md("13_run2_shot.md")),
        ("md", md("14_run3.md")),
        ("code", "run_case(ERROR_ENV_FILE, ERROR_SCHEDULE_FILE)"),
        ("md", md("15_run3_shot.md")),
    ]


def _png(name: str) -> str:
    """Base64 text of a screenshot, for a markdown cell attachment.

    Args:
        name: File name in ``report/screenshots``.

    Returns:
        Base64-encoded PNG.
    """
    return base64.b64encode((SCREENSHOTS / name).read_bytes()).decode("ascii")


def build() -> str:
    """Build the notebook JSON text.

    Returns:
        Notebook file content.
    """
    nb = nbformat.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    }
    for i, (kind, text) in enumerate(cells()):
        text = text.strip()
        if kind == "md":
            cell = nbformat.v4.new_markdown_cell(text)
            names = _ATTACHMENT.findall(text)
            if names:
                cell.attachments = {n: {"image/png": _png(n)} for n in names}
        else:
            cell = nbformat.v4.new_code_cell(text)
        cell.id = str(i)  # fixed ids, numbered as nbstripout does
        nb.cells.append(cell)
    return _ruff(nbformat.writes(nb) + "\n")


def _ruff(text: str) -> str:
    """Pass the notebook through ``ruff check --fix`` and ``ruff format``.

    Dropping the ``cep`` imports changes the import blocks, so ruff tidies
    them; doing it here keeps the lint job green on the generated file.

    Args:
        text: Notebook JSON.

    Returns:
        Fixed and formatted notebook JSON.
    """
    name = str(NOTEBOOK.relative_to(ROOT))
    for cmd in (["check", "--fix", "--quiet", "--exit-zero"], ["format"]):
        text = subprocess.run(
            ["ruff", *cmd, "--stdin-filename", name, "-"],
            input=text,
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
        ).stdout
    return text


def main(argv: list[str] | None = None) -> int:
    """Entry point; returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed notebook equals a fresh build",
    )
    args = parser.parse_args(argv)

    text = build()
    if args.check:
        if not NOTEBOOK.exists():
            print(f"FAIL: {NOTEBOOK.name} missing; run tools/build_notebook.py")
            return 1
        if NOTEBOOK.read_text(encoding="utf-8") != text:
            print(f"FAIL: {NOTEBOOK.name} is stale; run tools/build_notebook.py")
            return 1
        print(f"{NOTEBOOK.name} is up to date")
        return 0
    NOTEBOOK.write_text(text, encoding="utf-8")
    print(f"wrote {NOTEBOOK.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
