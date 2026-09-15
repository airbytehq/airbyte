---
name: source-snowflake-e2e-tests
description: Run the Airbyte protocol sweep for airbyte/source-snowflake:<tag> against the shared Snowflake integration account inside a per-run PROVEFIX_<run_id> schema (B3 remote-backend mode of db-harness-lib); prove-fix comparisons, cursor canary, orphan sweep.
---

# source-snowflake-e2e-tests

Remote end-to-end harness for `source-snowflake`. The shared
`db-harness-lib` orchestration runs protocol commands against a per-run schema
in the shared Snowflake integration account.

## Prerequisites

- Docker, [`uv`](https://docs.astral.sh/uv/), and `jq`.
- `gcloud` authenticated with read access to the GSM secret, or an existing
  `SNOWFLAKE_CONFIG_FILE`.
- A clone of `airbytehq/airbyte`.

## Layout

```
source-snowflake-e2e-tests/
├── SKILL.md
├── scripts/
│   ├── run.sh, sf.py
│   ├── fetch-config.sh, render-config.sh
│   ├── start-backend.sh, reset-databases.sh, stop-backend.sh
│   ├── apply-sql.sh, sweep-orphans.sh
│   └── ...
├── fixtures/configs/base.template.json, utc-session.template.json
├── fixtures/sql/00-cursor-canary-base.sql
├── fixtures/sql/01-cursor-canary-boundary-row.sql
└── cases/cursor-upper-bound.sh
```

## Isolation model

- Every run uses `PROVEFIX_<run_id>` and asserts that the schema is absent
  before both control and target runs.
- A marker owned by the run permits reuse of the same schema between canary
  phases; unmarked pre-existing schemas are refused.
- Control and target use the same schema with `--reset=fixture`; remote
  `--reset=backend` is rejected.
- Teardown drops the schema in the run's exit trap.
- `scripts/sweep-orphans.sh` lists or drops old `PROVEFIX_*` schemas.

The schema is owned by the scripts, while `sf.py` is the only code that talks
to Snowflake. The default config comes from GSM secret
`SECRET_SOURCE-SNOWFLAKE_KEY_PAIR__CREDS` in project
`dataline-integration-testing`; set `SNOWFLAKE_CONFIG_FILE` to reuse a fetched
config.

## Cursor upper-bound canary

The canary proves the cursor precision regression from airbytehq/airbyte#82705:

```bash
cases/cursor-upper-bound.sh
```

It compares fixed `1.1.1` with control `1.1.0` in two phases. Phase 1 runs the
initial sync on the control image with exact-microsecond base rows, producing
the checkpoint a user on the bad version would have. Phase 2 inserts a
sub-microsecond boundary row and replays that state against both versions:
1.1.0 loses the row because it floors the upper bound, while 1.1.1 emits it.

The harness reuses the `INTEGRATION_TEST_WAREHOUSE_DESTINATION` X-Small
warehouse shared with destination-snowflake integration tests. Never touch
schemas outside `PROVEFIX_*`.

## Gotchas

Snowflake uppercases identifiers, so use
`--cursor-field=UPDATED_AT --streams=CURSOR_CANARY`. Rendered configs contain
the private key; treat `REPRO_OUT` as 0600 material and never attach it.
TIMESTAMP_NTZ cursor bounds are bound as TIMESTAMP_LTZ by the JDBC driver and
compared through the session TIMEZONE; with the account default
(America/Los_Angeles), narrow incremental windows match nothing.
The harness sets `jdbc_url_params=TIMEZONE=UTC` so the canary isolates #82705;
this session-timezone behavior appears to be a separate connector bug worth
its own issue.
