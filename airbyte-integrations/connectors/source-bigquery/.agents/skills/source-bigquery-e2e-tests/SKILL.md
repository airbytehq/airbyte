---
name: source-bigquery-e2e-tests
description: Run the Airbyte protocol smoke sweep for airbyte/source-bigquery:<tag> against the shared BigQuery integration project inside a per-run PROVEFIX_<run_id> dataset (B3 remote-backend mode of db-harness-lib), with a dry-run orphan sweep.
---

# source-bigquery-e2e-tests

This harness runs the source-bigquery protocol regression sweep against an isolated dataset in a real BigQuery project. Orchestration comes from `airbyte-integrations/db-harness-lib`; the engine scripts own the dataset, fixtures, and credentials.

## Prerequisites

- `gcloud` with ambient access to Secret Manager in `GSM_PROJECT`.
- `bq` and `docker`.
- `airbyte-ops` (or `uvx airbyte-internal-ops`).
- A BigQuery service account with dataset create/delete, query, and source-read permissions in `BIGQUERY_PROJECT`.

Cloud Storage Read API coverage requires `airbyte-ops cloud connector regression-test --extra-env`, added in [airbyte-ops-mcp#349](https://github.com/airbytehq/airbyte-ops-mcp/pull/349). The shim defaults `BIGQUERY_AIRBYTE_EDITION` to `CLOUD` and adds `AIRBYTE_EDITION=CLOUD` when supported. Set `BIGQUERY_AIRBYTE_EDITION=''` to disable the check and injection. Older `airbyte-ops` versions warn and continue using the query API.

## Run

From this connector directory:

```bash
poe e2e-local --test-version=1.0.1
```

The Poe task forwards the shared harness flags; use `poe e2e-local --help` for the full list. Common options include `--command=check`, `--skip-read`, `--step-name=NAME`, `--keep-backend`, and `--reset=fixture`. Environment overrides include `REPRO_OUT`, `GSM_PROJECT`, `BIGQUERY_PROJECT`, `BIGQUERY_LOCATION`, `BIGQUERY_SECRET_NAME`, `BIGQUERY_CONFIG_FILE`, `AIRBYTE_OPS`, and `BIGQUERY_AIRBYTE_EDITION`.

## Dataset lifecycle

Each run creates `PROVEFIX_<run_id>` in `BIGQUERY_PROJECT` and records ownership in `$REPRO_OUT/.provefix-owned-PROVEFIX_<run_id>`. An existing dataset is reused only with that marker; otherwise the harness refuses to touch it and points to `sweep-orphans.sh`. The default teardown drops the owned dataset and verifies it is absent. `--reset=fixture` drops and recreates the run dataset between comparison sweeps. `sweep-orphans.sh --dry-run` lists old `PROVEFIX_*` datasets without deleting them; `--older-than-hours=N` defaults to 4.

`gcloud`/`bq` authentication uses `$REPRO_OUT/.gcloud`, separate from the ambient credentials used to fetch the GSM secret. The fetched service-account key and isolated auth directory are removed at teardown.

## Expected smoke result

Both runs pass CHECK, DISCOVER `smoke_table` and `smoke_view`, and READ three records from each stream. The installed CLI warns when it lacks `--extra-env`, so that run exercises only the query API. With `BIGQUERY_AIRBYTE_EDITION=CLOUD` and the #349 CLI, connector logs show `smoke_table` opening a Storage Read API session and `smoke_view` falling back to the query API because views are unsupported by the Storage Read API.

There is no bad-vs-fixed proof case yet: the 1.0.1 views fallback requires a service account without BigQuery Read Session User, and none exists in GSM.
