"""Generate the report's repository-inventory appendix (REQ-RPT-12, issue #30).

Writes ``report/latex/appendices/inventory_data.tex`` from the tracked files
(``git ls-files``), their docstrings/headings/contents and the "Repo map" and
"Frozen interfaces" blocks of ``AGENTS.md``. Nothing is typed in by hand, so the
appendix can be regenerated whenever the code changes::

    python tools/repo_inventory.py
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "latex" / "appendices" / "inventory_data.tex"

# Characters LaTeX treats specially, plus the few non-ASCII symbols that
# Times New Roman lacks and that occur in docstrings.
_TEX_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "→": r"$\to$",
    "≤": r"$\le$",
    "≥": r"$\ge$",
    "−": "-",
    "✓": r"$\checkmark$",
    "✗": r"$\times$",
}
_BREAK_AFTER = "/_.-"  # where a long file name may wrap in a table cell
_LANG = {
    ".py": "Python",
    ".md": "Markdown",
    ".tex": "TeX",
    ".png": "PNG",
    ".pdf": "PDF",
    ".txt": "text",
    ".yml": "YAML",
    ".ipynb": "notebook",
    ".json": "JSON",
    ".toml": "TOML",
}
# Binary files carry no text to read, so their role comes from their name.
_BINARY_ROLE = {
    "report/CS24045.pdf": "compiled report (PDF)",
    "report/latex/figures/rubric_filled.pdf": "grading rubric with members filled in",
    "report/figures/rubric_filled.png": "grading rubric with members filled in (PNG)",
    "report/figures/search_comparison.png": "UCS vs A* comparison plots",
}
_CATEGORIES = (
    ("Source code (src/cep/)", ("src/",)),
    ("Tests (tests/)", ("tests/",)),
    ("Tools and scripts (tools/)", ("tools/",)),
    ("Notebook (notebook/)", ("notebook/",)),
    ("Input data (data/)", ("data/",)),
    ("Report (report/)", ("report/",)),
    (
        "Documentation (docs/, top-level Markdown)",
        ("docs/", "README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md"),
    ),
)
_CONFIG_CATEGORY = "CI and configuration (.github/, config files)"


def tex_escape(text: str) -> str:
    """Escape LaTeX special characters in running text.

    Args:
        text: Raw text.

    Returns:
        Text safe to place in a LaTeX table cell or paragraph.
    """
    return "".join(_TEX_MAP.get(ch, ch) for ch in text).replace("--", "-{}-")


def tex_code(text: str) -> str:
    r"""Typeset a name or path in monospace with line-break opportunities.

    Args:
        text: Raw identifier or path.

    Returns:
        A ``\\texttt{...}`` string whose long names can wrap after ``/ _ . -``.
    """
    parts = []
    for ch in text:
        parts.append(_TEX_MAP.get(ch, ch))
        if ch in _BREAK_AFTER:
            parts.append(r"\allowbreak{}")
    return r"\texttt{" + "".join(parts) + "}"


def shorten(text: str, limit: int = 88) -> str:
    """Reduce a description to its first sentence and a maximum length.

    Args:
        text: Raw first line of a docstring, heading or comment.
        limit: Maximum number of characters kept.

    Returns:
        The first sentence, cut on a word boundary with an ellipsis if needed.
    """
    text = " ".join(text.replace("`", "").replace("**", "").split())
    text = re.split(r"\.\s+(?=[A-Z])", text, maxsplit=1)[0].rstrip(".")
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "…"


def tracked_files() -> list[str]:
    """List the tracked files of the repository.

    Returns:
        Repository-relative POSIX paths from ``git ls-files`` (ignored and
        untracked files are not included), sorted.
    """
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return sorted(line for line in out.splitlines() if line)


def repo_map() -> dict[str, str]:
    """Read the "Repo map" table of ``AGENTS.md``.

    Returns:
        Mapping from a path (as written in the table) to its stated purpose.
    """
    mapping: dict[str, str] = {}
    for line in (ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|", line)
        if match:
            mapping[match.group(1)] = match.group(2).replace("`", "").replace("**", "")
    return mapping


def frozen_names() -> set[str]:
    """Read the frozen-interface function names from ``AGENTS.md``.

    Returns:
        Names that start a line inside the "Frozen interfaces" code block.
    """
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    block = (
        text.split("## Frozen interfaces", 1)[1]
        .split("```python", 1)[1]
        .split("```", 1)[0]
    )
    return set(re.findall(r"^(\w+)\(", block, flags=re.MULTILINE))


def _first_comment(lines: list[str]) -> str:
    """Return the first descriptive ``#`` comment line of a file.

    Args:
        lines: File lines.

    Returns:
        Comment text without the marker, or an empty string.
    """
    for line in lines:
        if line.startswith("#!") or "TEX root" in line:
            continue
        stripped = line.lstrip("%# ").strip()
        if line.lstrip().startswith(("#", "%")) and stripped:
            return stripped
    return ""


def describe_file(rel: str, rmap: dict[str, str]) -> str:
    r"""Describe a tracked file from its own content.

    Args:
        rel: Repository-relative path.
        rmap: The ``AGENTS.md`` repo map (fallback description).

    Returns:
        A terse description (docstring, heading, ``\\section`` title, counts...).
    """
    path = ROOT / rel
    if rel in _BINARY_ROLE:
        return _BINARY_ROLE[rel]
    if path.suffix in {".png", ".pdf"}:
        return rmap.get(rel, f"{_LANG[path.suffix]} file")
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    name = path.name
    if path.suffix == ".py":
        doc = ast.get_docstring(ast.parse(text))
        if doc:
            return shorten(doc.splitlines()[0])
        target = ROOT / "src" / "cep" / name.removeprefix("test_")
        return (
            f"tests for src/cep/{target.name}" if target.exists() else "Python module"
        )
    if path.suffix == ".md":
        if rel == ".github/pull_request_template.md":
            heads = [x.lstrip("# ") for x in lines if x.startswith("## ")]
            return "pull request template: " + ", ".join(heads)
        for line in lines:
            if line.startswith("@"):
                return "imports " + line[1:]
            if line.startswith("#"):
                return shorten(line.lstrip("# "))
        comment = re.search(r"<!--\s*(.*?)\s*-->", text, flags=re.DOTALL)
        return shorten(
            comment.group(1) if comment else next((x for x in lines if x.strip()), "")
        )
    if path.suffix == ".tex":
        match = re.search(r"\\section\*?\{(.*?)\}", text)
        if match and rel.startswith(
            ("report/latex/chapters/", "report/latex/appendices/")
        ):
            return "section: " + shorten(match.group(1))
        return shorten(_first_comment(lines))
    if path.suffix == ".sh":
        return shorten(_first_comment(lines))
    if path.suffix == ".yml":
        if rel.startswith(".github/workflows/"):
            return shorten(_first_comment(lines))
        name_m = re.search(r"^name:\s*(.+)$", text, flags=re.MULTILINE)
        desc_m = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
        if name_m and desc_m:
            return shorten(f"issue template {name_m.group(1)}: {desc_m.group(1)}")
        return "YAML file"
    if path.suffix == ".ipynb":
        cells = json.loads(text)["cells"]
        kinds = Counter(c["cell_type"] for c in cells)
        return (
            f"submitted notebook: {kinds['code']} code and "
            f"{kinds['markdown']} markdown cells"
        )
    if path.suffix == ".toml":
        tools = sorted(
            {
                m.split(".")[1]
                for m in re.findall(r"^\[(tool\.[\w.]+)\]", text, flags=re.MULTILINE)
            }
        )
        return "project metadata; settings for " + ", ".join(tools)
    if path.suffix == ".json":
        return shorten("editor settings: " + ", ".join(json.loads(text)))
    if rel.startswith("data/") and name.startswith(("Environment", "Schedule")):
        return _describe_input(name, lines)
    if name == "requirements.txt":
        deps = [x for x in lines if x.strip() and not x.startswith("#")]
        return f"{len(deps)} Python dependencies"
    if name == ".gitignore":
        rules = [x for x in lines if x.strip() and not x.startswith("#")]
        return f"{len(rules)} ignore patterns"
    if name == ".gitattributes":
        return "git attributes: " + ", ".join(
            sorted({x.split()[0] for x in lines if x.strip()})
        )
    if name == "CODEOWNERS":
        rules = [x for x in lines if x.strip() and not x.startswith("#")]
        return f"code owners for {len(rules)} path patterns"
    return rmap.get(rel, "file")


def _describe_input(name: str, lines: list[str]) -> str:
    """Describe an environment or schedule input file from its numbers.

    Args:
        name: File name (``Environment*.txt`` or ``Schedule*.txt``).
        lines: File lines (formats of spec §5.2 and §6.3).

    Returns:
        A description with the grid size and obstacle count, or the slot and
        constraint counts.
    """
    if name.startswith("Environment"):
        return (
            f"environment input: {lines[0]} grid, {lines[1]} obstacles, "
            f"{lines[3]} dirty cells"
        )
    n_prec = int(lines[1])
    n_latest = int(lines[2 + n_prec])
    return (
        f"schedule input: {lines[0]} slots, {n_prec} precedence, "
        f"{n_latest} latest-slot constraints"
    )


def _summary(files: list[str]) -> str:
    """Summarise a set of files by type.

    Args:
        files: Paths directly inside one directory.

    Returns:
        For example ``"7 Python, 1 Markdown"``.
    """
    kinds = Counter(
        _LANG.get(Path(f).suffix, Path(f).name)
        for f in files
        if Path(f).name != ".gitkeep"
    )
    return ", ".join(f"{n} {k}" for k, n in sorted(kinds.items())) or "placeholder only"


def build_tree(files: list[str], rmap: dict[str, str]) -> str:
    """Build the directory tree (directories plus top-level files).

    Args:
        files: Tracked paths.
        rmap: The ``AGENTS.md`` repo map (purposes of directories).

    Returns:
        ASCII tree, one entry per line with a short comment.
    """
    dirs = sorted(
        {
            str(Path(*Path(f).parts[:i]))
            for f in files
            for i in range(1, len(Path(f).parts))
        }
    )
    entries: list[tuple[str, str, str]] = [("", ROOT.name + "/", "")]
    top = [f for f in files if "/" not in f]
    children: dict[str, list[str]] = {}
    for d in dirs:
        children.setdefault(str(Path(d).parent) if "/" in d else "", []).append(d)

    def walk(parent: str, depth: int) -> None:
        for d in children.get(parent, []):
            direct = [f for f in files if str(Path(f).parent) == d]
            note = _summary(direct) if direct else "subfolders"
            if rmap.get(d + "/"):
                note = shorten(rmap[d + "/"], 44)
            entries.append(("    " * depth, Path(d).name + "/", note))
            walk(d, depth + 1)

    walk("", 0)
    # Directories first, then the top-level files, like ``tree --dirsfirst``.
    for f in top:
        entries.append(("", f, shorten(describe_file(f, rmap), 44)))
    lines = []
    for i, (indent, name, note) in enumerate(entries):
        prefix = "" if i == 0 else indent + "|-- "
        left = prefix + name
        lines.append(f"{left:<34}{note}".rstrip())
    return "\n".join(lines)


def category_of(rel: str) -> str:
    """Pick the B.2 category of a file.

    Args:
        rel: Repository-relative path.

    Returns:
        The category title.
    """
    for title, prefixes in _CATEGORIES:
        if any(rel == p or rel.startswith(p) for p in prefixes):
            return title
    return _CONFIG_CATEGORY


def files_table(files: list[str], rmap: dict[str, str]) -> str:
    """Build the B.2 table (files grouped by category).

    Args:
        files: Tracked paths.
        rmap: The ``AGENTS.md`` repo map.

    Returns:
        LaTeX ``longtable`` source.
    """
    groups: dict[str, list[tuple[str, str]]] = {t: [] for t, _ in _CATEGORIES}
    groups[_CONFIG_CATEGORY] = []
    folded: dict[tuple[str, str], list[str]] = {}
    for rel in files:
        cat = category_of(rel)
        if Path(rel).name == ".gitkeep":
            folded.setdefault((_CONFIG_CATEGORY, "**/.gitkeep"), []).append(rel)
        elif rel.startswith("docs/spec/"):
            folded.setdefault((cat, "docs/spec/*"), []).append(rel)
        elif rel.startswith("notebook/markdown/"):
            folded.setdefault((cat, "notebook/markdown/*.md"), []).append(rel)
        elif rel.startswith("report/screenshots/"):
            folded.setdefault((cat, "report/screenshots/*.png"), []).append(rel)
        else:
            groups[cat].append((rel, describe_file(rel, rmap)))
    notes = {
        "docs/spec/*": "frozen specification PDFs and their checksums",
        "notebook/markdown/*.md": "markdown cells assembled by tools/build_notebook.py",
        "report/screenshots/*.png": "test-run screenshots (configuration, output)",
        "**/.gitkeep": "empty-directory placeholders",
    }
    for (cat, label), members in folded.items():
        groups[cat].append((f"{label} ({len(members)})", notes[label]))
    rows = [
        r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.45\linewidth}>{\raggedright\arraybackslash}p{0.52\linewidth}@{}}",
        r"\toprule",
        r"\textbf{File} & \textbf{Description} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{File} & \textbf{Description} (continued) \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endlastfoot",
    ]
    for title, items in groups.items():
        if not items:
            continue
        rows.append(
            rf"\multicolumn{{2}}{{@{{}}l}}{{\textbf{{{tex_escape(title)}}}}} \\*"
        )
        rows.append(r"\midrule")
        for name, desc in sorted(items):
            rows.append(rf"{tex_code(name)} & {tex_escape(shorten(desc, 66))} \\")
        rows.append(r"\addlinespace[3pt]")
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def _leading_comment(lines: list[str], lineno: int) -> str:
    """Return the ``#`` comment block directly above a 1-based line number.

    Args:
        lines: Source lines.
        lineno: Line of the statement (1-based).

    Returns:
        The joined comment text, or an empty string.
    """
    block: list[str] = []
    i = lineno - 2
    while i >= 0 and lines[i].lstrip().startswith("#"):
        block.insert(0, lines[i].lstrip("# ").strip())
        i -= 1
    return " ".join(block)


def module_entries(rel: str, frozen: set[str]) -> list[dict[str, object]]:
    """List classes, methods, functions and constants of a Python module.

    Args:
        rel: Repository-relative path of the module.
        frozen: Names of the frozen interfaces (marked with a dagger).

    Returns:
        Dicts with ``name``, ``kind``, ``doc``, ``private`` and ``frozen``,
        in source order.
    """
    text = (ROOT / rel).read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[dict[str, object]] = []

    def add(name: str, kind: str, doc: str, private: bool) -> None:
        out.append(
            {
                "name": name,
                "kind": kind,
                "doc": doc,
                "private": private,
                "frozen": name in frozen,
            }
        )

    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node) or ""
            add(
                node.name,
                "function",
                doc.splitlines()[0] if doc else "",
                node.name.startswith("_"),
            )
        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or ""
            add(
                node.name,
                "class",
                doc.splitlines()[0] if doc else "",
                node.name.startswith("_"),
            )
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and not sub.name.startswith("__"):
                    mdoc = ast.get_docstring(sub) or ""
                    add(
                        f"{node.name}.{sub.name}",
                        "method",
                        mdoc.splitlines()[0] if mdoc else "",
                        sub.name.startswith("_") or node.name.startswith("_"),
                    )
        elif rel.startswith("src/") and isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id.isupper()
                    or (
                        isinstance(target, ast.Name) and target.id.lstrip("_").isupper()
                    )
                ):
                    value = ast.get_source_segment(text, node.value) or ""
                    fallback = (
                        f"multi-line text ({value.count(chr(10)) + 1} lines)"
                        if "\n" in value
                        else "= " + value
                    )
                    desc = _leading_comment(lines, node.lineno) or fallback
                    add(target.id, "constant", desc, target.id.startswith("_"))
    return out


def count_tests(rel: str) -> int:
    """Count the test functions of a test module.

    Args:
        rel: Repository-relative path of the test file.

    Returns:
        Number of functions or methods named ``test_*``.
    """
    tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
    return sum(
        isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
        for n in ast.walk(tree)
    )


def code_table(files: list[str], rmap: dict[str, str]) -> str:
    """Build the B.3 code-reference table.

    Args:
        files: Tracked paths.
        rmap: The ``AGENTS.md`` repo map.

    Returns:
        LaTeX ``longtable`` source with one block per module.
    """
    frozen = frozen_names()
    rows = [
        r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.30\linewidth}p{0.09\linewidth}>{\raggedright\arraybackslash}p{0.55\linewidth}@{}}",
        r"\toprule",
        r"\textbf{Name} & \textbf{Kind} & \textbf{Description} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{Name} & \textbf{Kind} & \textbf{Description} (continued) \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endlastfoot",
    ]
    modules = [
        f for f in files if f.endswith(".py") and f.startswith(("src/cep/", "tools/"))
    ]
    for rel in modules:
        entries = module_entries(rel, frozen)
        if not entries:
            continue
        rows.append(
            rf"\multicolumn{{3}}{{@{{}}l}}{{\textbf{{{tex_escape(rel)}}}: "
            rf"{tex_escape(describe_file(rel, rmap))}}} \\*"
        )
        rows.append(r"\midrule")
        for entry in sorted(entries, key=lambda e: bool(e["private"])):
            name = tex_code(str(entry["name"])) + (
                r"\textsuperscript{\textdagger}" if entry["frozen"] else ""
            )
            doc = tex_escape(shorten(str(entry["doc"]), 64)) if entry["doc"] else "---"
            rows.append(rf"{name} & {entry['kind']} & {doc} \\")
        rows.append(r"\addlinespace[3pt]")
    tests = [f for f in files if f.startswith("tests/") and f.endswith(".py")]
    rows.append(r"\multicolumn{3}{@{}l}{\textbf{tests/}: one row per test file} \\*")
    rows.append(r"\midrule")
    for rel in tests:
        rows.append(
            rf"{tex_code(rel)} & {count_tests(rel)} tests & "
            rf"{tex_escape(describe_file(rel, rmap))} \\"
        )
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def _glue_headings(tex: str) -> str:
    """Forbid a page break between a group heading row and its first row.

    Args:
        tex: Generated LaTeX.

    Returns:
        LaTeX whose heading rows are glued to the row below.
    """
    # booktabs' own \midrule glue is a legal break point, so draw an unbreakable rule.
    rule = (
        "\\noalign{\\nobreak\\vskip\\aboverulesep\\hrule height\\lightrulewidth"
        "\\nobreak\\vskip\\belowrulesep\\nobreak}"
    )
    return tex.replace("\\\\*\n\\midrule", "\\\\*\n" + rule)


def build() -> str:
    """Assemble the generated LaTeX of appendix sections B.1 to B.3.

    Returns:
        The full content of ``inventory_data.tex``.
    """
    files = tracked_files()
    rmap = repo_map()
    return _glue_headings(
        "\n".join(
            [
                "% Generated by tools/repo_inventory.py (REQ-RPT-12); do not edit.",
                r"\subsection{Repository layout}",
                r"\begingroup\small\linespread{1}\selectfont\renewcommand{\arraystretch}{0.92}",
                r"\begin{verbatim}",
                build_tree(files, rmap),
                r"\end{verbatim}",
                r"\endgroup",
                "",
                r"\subsection{Files by category}",
                r"\begingroup\small\linespread{1}\selectfont\renewcommand{\arraystretch}{0.92}",
                files_table(files, rmap),
                r"\endgroup",
                "",
                r"\subsection{Code reference}",
                r"Names marked with a dagger\footnote{\textdagger{} Frozen "
                r"interface (AGENTS.md, "
                r"``Frozen interfaces''): changed only through an approved issue "
                r"labelled "
                r"\texttt{frozen-interface}; the CI job \texttt{interface} checks "
                r"names and "
                r"parameter order.} are frozen interfaces. Private helpers "
                r"(leading underscore) "
                r"follow the public names of each module. A dash means the code "
                r"has no docstring.",
                r"\begingroup\small\linespread{1}\selectfont\renewcommand{\arraystretch}{0.92}",
                code_table(files, rmap),
                r"\endgroup",
                "",
            ]
        )
    )


def main() -> None:
    """Write ``inventory_data.tex``."""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
