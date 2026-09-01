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
  `apply-sql.sh`, `reset-databases.sh`, and `stop-backend.sh`.
- `DEFAULT_CONFIG_TEMPLATE`: engine's default config template, required
  unless `--config-template` is supplied.
- `DEFAULT_FIXTURE`: engine's default SQL fixture, required unless an
  explicit `--fixture` is supplied or `--skip-fixtures` is used.
- `BACKEND_NAME`: backend container name, required by the config renderer.

The engine scripts own backend lifecycle and fixture application. The
library scripts own protocol orchestration, catalog derivation, config
rendering, and state extraction. `BACKEND_NAME` and the other usual harness
environment variables may be overridden by callers for test isolation.

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
