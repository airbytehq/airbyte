> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to `source-snowflake`

This file is connector-specific. For general Airbyte contribution guidance,
see the repo-root [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) and the
[connector contribution guide](https://docs.airbyte.com/connector-development/).

`source-snowflake` is a Kotlin / bulk-CDK connector. Standard local commands:

```bash
./gradlew :airbyte-integrations:connectors:source-snowflake:test
./gradlew :airbyte-integrations:connectors:source-snowflake:assemble
./gradlew :airbyte-integrations:connectors:source-snowflake:dockerBuildx
```

## Reproducing bugs

The remote-backend harness for this connector is documented in
[`.agents/skills/source-snowflake-e2e-tests/SKILL.md`](.agents/skills/source-snowflake-e2e-tests/SKILL.md).
It creates a per-run `PROVEFIX_<run_id>` schema in the shared Snowflake
integration account using a GSM key-pair secret; there is no local container,
and `--reset=backend` is rejected. The `poe e2e-local` task is the entrypoint.

The worked example is
`.agents/skills/source-snowflake-e2e-tests/cases/cursor-upper-bound.sh`.
After a run, check for leaked schemas with
`sweep-orphans.sh --older-than-hours=0 --dry-run`.

## Troubleshooting

Files under `airbyte-integrations/connectors/source-snowflake/`, including
`.agents/`, are treated as connector changes by CI. The matrix detector
requires a `dockerImageTag` bump and a changelog entry when these files
change. Do not edit metadata solely to bypass this check without confirming
the required versioning decision.
