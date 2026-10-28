> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to `source-bigquery`

This file is connector-specific. For build and test commands, see
[CONTRIBUTING.md](CONTRIBUTING.md).

`source-bigquery` is a Bulk CDK connector.

## Reproducing bugs

The remote-backend harness is documented in
[`.agents/skills/source-bigquery-e2e-tests/SKILL.md`](.agents/skills/source-bigquery-e2e-tests/SKILL.md).
The `poe e2e-local` task creates a per-run `PROVEFIX_*` dataset in the shared
BigQuery integration project using a GSM service-account secret, then removes
it during teardown. Check cleanup in the run output; use
`.agents/skills/source-bigquery-e2e-tests/scripts/sweep-orphans.sh --dry-run`
to inspect old datasets without deleting them.
