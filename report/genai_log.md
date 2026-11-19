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
| 2026-11-19 | Huzaifa | Claude Code (Claude Opus 5.5) | Authored CSP solver in src/cep/csp.py (is_consistent, MRV+degree per DEC-05, forward checking with copy-based restoration, LCV, backtracking) and tests/test_csp.py (incl. brute-force oracle) | #17 #18 #19 #20 #21 |
