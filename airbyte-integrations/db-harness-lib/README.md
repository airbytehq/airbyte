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

## Scripts

- `run.sh` runs the spec, check, discover, and read sweep while preserving
  the documented flags, exit codes, and artifact layout.
- `run-protocol-cmd.sh` invokes `airbyte-ops` for one protocol command.
- `make-catalog.sh` derives a configured catalog from discover output.
- `render-config.sh` substitutes the backend address using an overridable
  `CONFIG_HOST_JQ` jq expression.
- `extract-state.py` extracts Airbyte state messages from JSONL output.
