#!/usr/bin/env bash
# Run the CI checks locally (plan §9). CI calls the same subcommands.
#
#   tools/ci_local.sh                 # all jobs except traceability
#   tools/ci_local.sh <job> [...]     # lint test robustness interface notebook
#                                     # ai-boundary spec-frozen traceability
#
# Env: BASE_REF  ai-boundary range start (default: origin/main)
#      PR_BODY   traceability input (CI sets it from the pull request)
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
NOTEBOOK_DIR=notebook

has_notebooks() { compgen -G "$NOTEBOOK_DIR/*.ipynb" >/dev/null; }

# pytest exit code 5 = "no tests collected" -> treat as a skip while stubs are empty.
run_pytest() {
  set +e; "$PY" -m pytest "$@"; local rc=$?; set -e
  if [ "$rc" -eq 5 ]; then echo "SKIP: no tests collected"; return 0; fi
  return "$rc"
}

job_lint() {
  ruff check .
  ruff format --check .
  if has_notebooks; then
    nbstripout --verify "$NOTEBOOK_DIR"/*.ipynb
  else
    echo "SKIP nbstripout: no notebook yet"
  fi
}

job_test() {
  run_pytest tests/ --ignore=tests/test_properties.py --cov=src/cep
}

job_robustness() {
  if [ -f tests/test_properties.py ]; then
    run_pytest tests/test_properties.py
  else
    echo "SKIP: tests/test_properties.py not present yet"
  fi
}

# Frozen signatures, docs/plan.md §4. Only names and parameter order are frozen;
# type hints may be added.
job_interface() {
  "$PY" - <<'PYEOF'
import ast, pathlib, sys

FROZEN = {
    "src/cep/search.py": {
        "get_successors": ["state", "grid"],
        "goal_test": ["state", "goal_state"],
        "path_cost": ["path"],
        "heuristic": ["state", "goal_state"],
        "search": ["grid", "start", "goal", "algorithm"],
    },
    "src/cep/csp.py": {
        "select_unassigned_variable": ["assignment", "domains", "constraints"],
        "order_domain_values": ["variable", "assignment", "domains", "constraints"],
        "is_consistent": ["variable", "value", "assignment", "constraints"],
        "forward_check": ["variable", "value", "assignment", "domains", "constraints"],
        "backtracking_search": ["variables", "domains", "constraints"],
    },
    "src/cep/integrate.py": {
        "execute_schedule": ["grid", "charging_station", "schedule", "algorithm"],
    },
}
errors = []
for path, funcs in FROZEN.items():
    p = pathlib.Path(path)
    if not p.exists():
        errors.append(f"{path}: missing")
        continue
    tree = ast.parse(p.read_text(), filename=path)
    defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for name, params in funcs.items():
        node = defs.get(name)
        if node is None:
            errors.append(f"{path}: top-level function {name}() missing")
            continue
        a = node.args
        got = [x.arg for x in a.posonlyargs + a.args]
        if got != params or a.vararg or a.kwarg or a.kwonlyargs:
            errors.append(f"{path}: {name}({', '.join(got)}) != frozen {name}({', '.join(params)})")
for e in errors:
    print("INTERFACE:", e)
if errors:
    sys.exit(1)
print("interface: all frozen signatures match plan §4")
PYEOF
}

job_notebook() {
  "$PY" tools/build_notebook.py --check
  if has_notebooks; then
    "$PY" -m pytest --nbmake "$NOTEBOOK_DIR"/
  else
    echo "SKIP nbmake: no notebook yet"
  fi
}

# Plan §2: commits carrying an AI Co-Authored-By trailer may not touch these paths.
# The scaffold commit (the one that creates src/cep/) is exempt.
job_ai_boundary() {
  local base="${BASE_REF:-origin/main}" range commits bad=0
  if git rev-parse -q --verify "$base^{commit}" >/dev/null; then
    range="$base..HEAD"
  else
    echo "ai-boundary: base '$base' not found; checking all commits"
    range="HEAD"
  fi
  commits=$(git rev-list "$range")
  for c in $commits; do
    git log -1 --format=%B "$c" \
      | grep -qiE '^co-authored-by:.*(claude|anthropic|copilot|openai|chatgpt|codex|gemini|cursor)' \
      || continue
    # Scaffold exemption: parent has no src/cep/ (only true for the scaffold commit).
    if ! git cat-file -e "$c^:src/cep" 2>/dev/null && git cat-file -e "$c:src/cep" 2>/dev/null; then
      echo "ai-boundary: $c is the scaffold commit (exempt)"
      continue
    fi
    local files
    files=$(git diff-tree --no-commit-id --name-only -r --root "$c")
    local hits
    hits=$(echo "$files" | grep -E '^(src/|tests/|data/|tools/gen_env\.py$|notebook/.*\.ipynb$|report/)' \
                         | grep -vE '^report/genai_log\.md$' || true)
    if [ -n "$hits" ]; then
      echo "ai-boundary: AI-co-authored commit $c touches forbidden paths:"
      echo "$hits" | sed 's/^/  /'
      bad=1
    fi
  done
  [ "$bad" -eq 0 ] && echo "ai-boundary: OK"
  return "$bad"
}

job_spec_frozen() {
  (cd docs/spec && sha256sum --check --strict SHA256SUMS)
  local listed actual
  listed=$(awk '{print $2}' docs/spec/SHA256SUMS | sed 's/^\*//' | sort)
  actual=$(cd docs/spec && ls -1 | grep -v '^SHA256SUMS$' | sort)
  if [ "$listed" != "$actual" ]; then
    echo "spec-frozen: docs/spec/ file list differs from SHA256SUMS"; return 1
  fi
}

job_traceability() {
  local body="${PR_BODY:-}"
  echo "$body" | grep -qE 'REQ-[A-Z]+(-[0-9]+)?' \
    || { echo "traceability: PR body cites no REQ- ID"; return 1; }
  echo "$body" | grep -qiE '^[[:space:]*-]*\**model used\**[[:space:]]*:[[:space:]]*\S' \
    || { echo "traceability: PR body has no filled 'Model used:' line"; return 1; }
  echo "traceability: OK"
}

ALL="lint test robustness interface notebook ai-boundary spec-frozen"
jobs=("$@"); [ ${#jobs[@]} -eq 0 ] && read -ra jobs <<<"$ALL"
fail=0
for j in "${jobs[@]}"; do
  echo "=== $j"
  if "job_${j//-/_}"; then echo "--- $j: PASS"; else echo "--- $j: FAIL"; fail=1; fi
done
exit "$fail"
