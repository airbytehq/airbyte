# Database e2e harness library

This library contains the engine-independent orchestration for local
database connector end-to-end tests. Connector skills keep the engine
implementation, fixtures, and configuration templates in their own
directories, then invoke `scripts/run.sh` through a small engine shim.
Because this library is outside connector directories, changes here do not
require connector version bumps.

## Engine contract

An engine shim must export:

- `CONNECTOR`: connector image name without the `airbyte/` prefix.
- `ENGINE_SCRIPTS_DIR`: directory containing `start-backend.sh`,
  `apply-sql.sh`, and `reset-databases.sh`. An engine-specific
  `stop-backend.sh` is optional; the library's default is used when it is
  absent.
- `DEFAULT_CONFIG_TEMPLATE`: engine's default config template, required
  unless `--config-template` is supplied.
- `DEFAULT_FIXTURE`: engine's default SQL fixture, required unless an
  explicit `--fixture` is supplied or `--skip-fixtures` is used.
- `BACKEND_NAME`: backend container name, required by the config renderer.

The engine scripts own backend startup, fixture application, and any
engine-specific teardown. The library's default teardown removes the
backend container when no engine-specific `stop-backend.sh` is provided.
The library scripts own protocol orchestration, catalog derivation, config
rendering, and state extraction. `BACKEND_NAME` and the other usual harness
environment variables may be overridden by callers for test isolation.

## Getting a target image

To test a fix that has not merged yet, publish a pre-release from its PR with
the Airbyte Ops MCP tool `publish_connector_to_airbyte_registry` (the
[`publish-connector-prerelease`](https://github.com/airbytehq/ai-skills/tree/main/.agents/skills/publish-connector-prerelease)
skill in `airbytehq/ai-skills` covers the invocation), and pass the resulting
`<version>-preview.<7-char-sha>` tag as `--test-version`. The harness pulls
any published tag and only builds from the checkout when `--test-version` is
literally `dev`, so this skips a cold Gradle build entirely and gives
reviewers a tag they can re-run against. Build locally with the connector's
`./gradlew :airbyte-integrations:connectors:<connector>:dockerBuildx` only for
code that is not on a pushed PR branch.

## Minimal engine shim example

A connector-specific skill can keep its engine scripts and fixtures while
delegating orchestration to this library:

```bash
#!/usr/bin/env bash
# PostgreSQL engine shim; orchestration lives in db-harness-lib.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"
export CONNECTOR=source-postgres
export ENGINE_SCRIPTS_DIR="$SKILL_DIR/scripts"
export DEFAULT_CONFIG_TEMPLATE="$SKILL_DIR/fixtures/configs/base.template.json"
export DEFAULT_FIXTURE="$SKILL_DIR/fixtures/sql/00-init-base.sql"
export BACKEND_NAME="${BACKEND_NAME:-source-postgres-db-backend}"

exec "$REPO_ROOT/airbyte-integrations/db-harness-lib/scripts/run.sh" "$@"
```

For an engine whose config places the host differently, override the jq
mutation used by the renderer:

```bash
export CONFIG_HOST_JQ='.host = $h | .port = 5432'
```

## Scripts

- `run.sh` runs the spec, check, discover, and read sweep while preserving
  the documented flags, exit codes, and artifact layout.
- `run-protocol-cmd.sh` invokes `airbyte-ops` for one protocol command.
- `make-catalog.sh` derives a configured catalog from discover output.
- `render-config.sh` substitutes the backend address using an overridable
  `CONFIG_HOST_JQ` jq expression.
- `extract-state.py` extracts Airbyte state messages from JSONL output.
