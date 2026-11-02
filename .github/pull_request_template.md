<!-- See AGENTS.md "Workflow". One issue per PR, branch `<issue#>-<short-slug>`. -->

Closes #

**REQ-IDs:** <!-- e.g. REQ-SRCH-05, REQ-SRCH-06 -->

## What changed
<!-- One or two sentences. -->

## Tests run
<!-- Paste the tail of `tools/ci_local.sh` and any extra commands. -->
```
tools/ci_local.sh
```

**Model used:** <!-- none | <model name> (for: <what it was used for>) -->

## Done checklist
- [ ] Cites issue + REQ-IDs
- [ ] `tools/ci_local.sh` passes locally
- [ ] Docstrings on new functions; comments explain *why*
- [ ] No hardcoded paths/coordinates outside `data/` and `tests/fixtures/`
- [ ] Frozen interfaces unchanged (or `frozen-interface` issue approved)
- [ ] "Model used" field filled; AI use logged in `report/genai_log.md`
