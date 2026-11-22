
# Generative AI use log

Every use of a Generative AI tool is logged here (AGENTS.md). Feeds the
report's "Generative AI Use Declaration" (spec §8.2).

| Date | Person | Tool / model | Purpose | Issue / PR |
|---|---|---|---|---|
| 2026-11-02 | Qazi | Claude Code (Claude Opus 5.5) | Repo scaffold: layout, configs, CI, templates, AGENTS.md, src/cep stubs (signatures + spec docstrings only); labels, milestones, issues | #1 |
| 2026-11-02 | Qazi | Claude Code (Claude Opus 5.5) | Fill GitHub usernames in CODEOWNERS / plan.md / AGENTS.md; mark plan approved; fix repo line in plan.md | #1 |
| 2026-11-08 | Qazi | Claude Code (Claude Opus 5.5) | Draft docs/requirements.md (REQ-IDs from spec); address review: team-choice tags, DEC-01…05 in decisions.md, issues #38–#40 | #2 |
| 2026-11-02 | Qazi | Claude Code (Claude Opus 5.5) | Reassign #5, #8, #10 Ashar → Qazi in plan.md / CODEOWNERS / AGENTS.md / issues | #5 #8 #10 |
| 2026-11-08 | Qazi | Claude Code (Claude Opus 5.5) | Fix Ashar's username in CODEOWNERS / AGENTS.md / plan.md | #35 |
| 2026-11-08 | Qazi | Claude Code (Claude Opus 5.5) | Address review on #34: Schedule*.txt + env.py owners, dedupe gen_env rule, plan rubric column, open items, model names in this log | #34 |
| 2026-11-08 | Qazi | Claude Code (Claude Opus 5.5) | Reschedule milestones (GitHub + plan.md); address review on #37 | #41 |
| 2026-11-18 | Qazi | Claude Code (Claude Opus 5.5) | Reassign #3, #4, #9 → Qazi; Ashar → tests + report; lead review change + 2-day schedule in plan.md / AGENTS.md / CODEOWNERS; present options and record DEC-04, DEC-05 | #42 #39 #40 |
| 2026-11-18 | Qazi | Claude Code (Claude Opus 5.5) | Lift AI code-authoring restriction: AGENTS.md, plan §2/§9, ai-boundary now checks docs/spec/ only, PR template | #44 |
| 2026-11-18 | Qazi | Claude Code (Claude Opus 5.5) | Internal types: design options, DEC-06, AGENTS.md Internal types section; authored Grid/Constraints/ACTIONS/ALGORITHMS/initial_domains in src/cep/env.py (after #44) | #3 |
| 2026-11-18 | Qazi | Claude Code (Claude Opus 5.5) | Listed parser spec gaps, recorded DEC-07–DEC-13; authored parse_environment/load_environment + InputError in src/cep/env.py | #4 |
| 2026-11-18 | Qazi | Claude Code (Claude Opus 5.5) | Authored parse_schedule/load_schedule in src/cep/env.py (rules DEC-07–DEC-10, DEC-12, DEC-13) | #5 |
| 2026-11-18 | Qazi | Claude Code (Claude Opus 5.5) | Found and fixed tools/ci_local.sh ignoring set -e inside jobs (lint passed with ruff errors); added to PR #48 at Qazi's request | #5 |
| 2026-11-18 | Qazi | Claude Code (Claude Opus 5.5) | Designed + verified own Environment.txt/Schedule.txt and Environment_Error.txt/Schedule_Error.txt (unreachable D5); throwaway BFS + brute-force checks, not committed | #8 #9 #10 |
| 2026-11-19 | Mujtaba | Claude Code (Claude Opus 5.5) | Authored get_successors/goal_test/path_cost/heuristic and UCS/A* search (shared priority queue, start==goal, no path) in src/cep/search.py + tests/test_search.py | #11 #12 #13 #14 |
| 2026-11-19 | Mujtaba | Claude Code (Claude Opus 5.5) | Drafted heuristic justification (admissible + consistent) notebook markdown + report paragraph — AI-written prose, declare in report | #15 |
| 2026-11-19 | Mujtaba | Claude Code (Claude Opus 5.5) | Authored src/cep/compare.py, tools/compare_search.py, tests/test_compare.py, comparison tables/plot and analysis draft | #16 |
| 2026-11-21 | Ashar | ChatGPT (GPT-6) | Reviewed and updated environment parser tests; added grid-cell, reachability, overlap, sample-file and invalid-input checks; removed duplicate root Environment.txt | #7 / #55 |
| 2026-11-20 | Ashar | ChatGPT (GPT-6) | AI-assisted implementation and validation of random environment and schedule generator; tested four modes, seeded reproducibility, custom dimensions, and code quality | #6 |
| 2026-11-19 | Huzaifa | Claude Code (Claude Opus 5.5) | Authored CSP solver in src/cep/csp.py (is_consistent, MRV+degree per DEC-05, forward checking with copy-based restoration, LCV, backtracking) and tests/test_csp.py (incl. brute-force oracle) | #17 #18 #19 #20 #21 |
| 2026-11-20 | Huzaifa | Claude Code (Claude Opus 5.5) | Resolved merge conflict in report/genai_log.md on PR #52 (kept all rows) | #52 |
| 2026-11-21 | Qazi | Claude Code (Claude Opus 5.5) | Authored execute_schedule, run_integration, plan_and_execute, schedule_from_assignment in src/cep/integrate.py + tests/test_integrate.py; recorded DEC-14 (#51) and DEC-15 | #23 #51 |
| 2026-11-20 | Huzaifa | Claude Code (Claude Opus 5.5) | Resolved merge conflict in report/genai_log.md on PR #52 (kept all rows) | #52 |
| 2026-11-21 | Qazi | Claude Code (Claude Opus 5.5) | Authored check_schedule / format_schedule / format_schedule_proof in src/cep/render.py + tests/test_render.py | #22 |
| 2026-11-21 | Qazi | Claude Code (Claude Opus 5.5) | Authored format_grid / format_legs / format_result in src/cep/render.py + tests | #24 |
| 2026-11-21 | Qazi | Claude Code (Claude Opus 5.5) | Authored tools/build_notebook.py, notebook/markdown/* cells (AI-written prose — declare in report), generated notebook/CS24045.ipynb; quoted IntegrationResult annotation in render.py so code cells can be ordered by section | #27 |
| 2026-11-21 | Qazi | Claude Code (Claude Opus 5.5) | Executed notebook test runs 1–3, rendered report/screenshots/run*.png from the real outputs (throwaway Playwright script, not committed), embedded them as notebook cell attachments via tools/build_notebook.py | #26 |
| 2026-11-21 | Qazi | Claude Code (Claude Opus 5.5) | Drafted the report (AI-written prose — declared in report §9) from code, decision log and measured runs; converted to LaTeX (report/latex/, Tectonic); tools/fill_rubric.py fills the rubric title page | #28 #29 #30 |
| 2026-11-22 | Qazi | Claude Code (Claude Opus 5.5) | Report §6: input files as verbatim text, outputs as separate per-algorithm screenshots (re-executed notebook); Tectonic font-loading fix | #28 #30 |
| 2026-11-22 | Qazi | Claude Code (Claude Opus 5.5) | Built the report in Google Docs (CS-323 - OEL Report) via the Docs API: text, styles, tables, 11 images, landscape rubric page; AI-written prose declared in report §9 | #28 #29 #30 |
| 2026-11-22 | Qazi | Claude Code (Claude Opus 5.5) | Switched grid, slot table and UCS vs A* tables to tabulate (render.py, compare.py, build_notebook.py, tests, requirements.txt) | #63 |
| 2026-11-22 | Qazi | Claude Code (Claude Sonnet 5.5) | Report §6: 12 screenshots (config + schedule + UCS + A* for runs 1–3) rendered with headless Firefox from the freshly executed notebook and the real input files; replaced verbatim config blocks by figures; fancyhdr header and "Page X of Y" footer; overfull-line fixes; rebuilt report/CS24045.pdf | #30 |
| 2026-11-22 | Qazi | Claude Code (Claude Sonnet 5.5) | Report opening block restyle (left-aligned kicker/title/team/notebook/note), table of contents page 1, two-line NED header and three-part footer | #30 |
| 2026-11-22 | Qazi | Claude Code (Claude Sonnet 5.5) | Repository inventory appendix (A) + tools/repo_inventory.py; AI declaration kept as Section 9 before the appendix | #30 |
| 2026-11-22 | Qazi | Claude Code (Claude Sonnet 5.5) | Run-guide appendix A (Linux steps verified in a fresh venv), repository inventory moved to appendix B, TOC marker for A, report/submission/requirements.txt | #30 #31 |
