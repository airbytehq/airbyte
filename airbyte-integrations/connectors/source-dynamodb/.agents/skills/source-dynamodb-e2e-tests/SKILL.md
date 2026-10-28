---
name: source-dynamodb-e2e-tests
description: Stand up a local DynamoDB Local backend, apply JSON fixtures, and sweep the Airbyte protocol commands (spec → check → discover → read) against airbyte/source-dynamodb:<tag> for ad-hoc end-to-end testing. Use when you need a deterministic, throwaway local environment for a cursor-incremental source-dynamodb test or prove-fix comparison.
---

# source-dynamodb-e2e-tests

Local end-to-end test harness for `source-dynamodb`. The engine-independent
orchestration lives in
[`airbyte-integrations/db-harness-lib/`](../../../../../db-harness-lib/);
this skill keeps the DynamoDB Local backend lifecycle scripts, fixtures, and
config templates. It stands up a DynamoDB Local container named
`source-dynamodb-db-backend`, applies JSON fixtures with the AWS CLI, and runs
Airbyte protocol commands against any `airbyte/source-dynamodb:<tag>` image
via `airbyte-ops cloud connector regression-test`.

Scope: no CDC mode exists; incremental reads use a user-defined cursor
attribute. Assume-role / IAM / STS behavior is not covered: DynamoDB Local
does not provide STS, and the connector's `endpoint` only overrides the
DynamoDB client, so a published connector image cannot send AssumeRole
requests to this emulator. State this limitation in the evidence plan rather
than claiming coverage.

## When to use this skill

- Reproducing a `source-dynamodb` bug locally without AWS credentials.
- Sweeping `spec` → `check` → `discover` → `read`, or running one of them,
  against any `airbyte/source-dynamodb:<tag>` for connector development.
- Proving a fix by comparing a target image with a control image.

## Prerequisites

- Docker.
- [`uv`](https://docs.astral.sh/uv/). `uv tool install
airbyte-internal-ops` puts `airbyte-ops` on `$PATH`; alternatively prefix
  every call with `uvx airbyte-internal-ops`.
- `jq`.
- A clone of `airbytehq/airbyte`.

You do not need AWS, IAM, or Cloud credentials. Local-only mode (no
`--connection-id`) reads everything from local files.

## Layout

```
source-dynamodb-e2e-tests/
├── SKILL.md
├── scripts/
│   ├── aws-cli.sh              # AWS CLI container and backend bridge-IP helpers
│   ├── start-backend.sh        # docker run DynamoDB Local with -sharedDb
│   ├── apply-sql.sh            # delete/create tables and put fixture items
│   ├── reset-databases.sh      # delete every table
│   └── run.sh                  # engine shim to db-harness-lib orchestration
└── fixtures/
    ├── configs/
    │   └── base.template.json  # user credentials, region, endpoint placeholder
    └── json/
        ├── 00-init-base.json   # sample with a numeric cursor and three items
        ├── attribute-types.json
        └── empty-table.json
```

`apply-sql.sh` keeps the db-harness-lib engine entrypoint name, but DynamoDB
fixtures are JSON documents, not SQL. Each fixture has a `tables` array. Each
table entry contains a `create` object accepted by `CreateTable
--cli-input-json` and an `items` array in DynamoDB attribute-value JSON:

```json
{
  "tables": [
    {
      "create": {
        "TableName": "sample",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST"
      },
      "items": [{"id": {"S": "e1"}, "seq": {"N": "1"}}]
    }
  ]
}
```

## Conventions

- Container name: `source-dynamodb-db-backend`. Override via
  `BACKEND_NAME=…` only for parallel test isolation; don't use customer
  connection names.
- No authentication. The config uses dummy `User` credentials and
  `us-east-1`; DynamoDB Local does not authenticate them.
- `-sharedDb` is required. Without it, DynamoDB Local namespaces tables by
  access key and region, so tables created by the fixture client can be
  invisible to the connector client.
- Working directory for rendered configs and run output:
  `${REPRO_OUT:-/tmp/source-dynamodb-repro}`, laid out as
  `$REPRO_OUT/<step-name>/{config.json,configured_catalog.json,<command>/}`.
- Both containers share Docker's default `bridge` network. The engine shim
  sets `CONFIG_HOST_JQ` so the shared
  [`render-config.sh`](../../../../../db-harness-lib/scripts/render-config.sh)
  rewrites `.endpoint` to `http://<bridge-ip>:8000` at runtime. The AWS CLI
  helper resolves the same bridge IP for its endpoint.
- DynamoDB Local is pinned to `amazon/dynamodb-local:3.3.2`. Override with
  `BACKEND_IMAGE=…` for a version-specific reproduction. The AWS CLI helper
  image is pinned to `amazon/aws-cli:2.38.2`; override with
  `AWS_CLI_IMAGE=…`.
- `attribute-types.json` exercises DynamoDB attribute-value families and a
  composite-key table. The connector's source-defined primary key is the
  partition key only; its sort key is not part of that primary key.

## Usage

`scripts/run.sh` is the only supported entrypoint. It performs the whole
sequence — start the backend, apply the fixtures, render the config, run
`spec` → `check` → `discover`, derive the configured catalog from that
`discover` output, run `read`, and tear down on exit:

```bash
cd airbyte-integrations/connectors/source-dynamodb

# Single version, full sweep.
poe e2e-local --test-version=0.4.1

# Target vs. control comparison.
poe e2e-local --test-version=0.4.1 --control-version=0.3.11 --reset=fixture

# One command only.
poe e2e-local --command=read --test-version=0.4.1
```

The sweep runs every command against the backend and reports each result
rather than stopping at the first failure, then prints a summary table. Under
CI the table is also appended to `$GITHUB_STEP_SUMMARY`.

Prefer a published target image for code on a pushed PR branch (publish a
pre-release with the Airbyte Ops MCP tool
`publish_connector_to_airbyte_registry` and pass the resulting
`<version>-preview.<7-char-sha>` tag as `--test-version`). See
[Getting a target image](../../../../../db-harness-lib/README.md#getting-a-target-image).
All other `run.sh` options (`--command`, `--fixture`, `--skip-fixtures`,
`--config-template`, `--catalog`, `--state=PATH`, `--reset`, `--expect-*`,
`--min-records`, …) are documented in the
[db-harness-lib README](../../../../../db-harness-lib/README.md) and
`poe e2e-local --help`.

## Common gotchas

- **DynamoDB key attributes.** `AttributeDefinitions` contains only the
  table's key attributes; non-key attributes such as `seq` and `label` appear
  in fixture items and are discovered by sampling them.
- **Sampled attributes.** Discovery samples table items and unions the
  attributes it sees. Keep at least one item with each field you want in the
  catalog. A field missing from an item is a useful missing-attribute case,
  but it may not be emitted if it is absent from every sampled item.
- **Configured-catalog nulls.** DynamoDB discover omits `namespace`,
  `source_defined_cursor`, and `is_resumable`, and 0.4.0 accepts them absent;
  it rejects `namespace: null`. Keep them omitted through an Airbyte Ops build
  that serializes configured catalogs with `exclude_none=True`; no shared
  catalog-generator defaults are needed.
- **Empty tables.** The connector discovers key attributes from
  `DescribeTable` when there are no items to sample, so an empty table remains
  in the catalog with its key fields.
- **Comparison catalogs.** Use `--reset=fixture` for comparisons where
  discovery output changes between image tags. In particular, for the
  integer-cursor regression below, the old tag discovers `seq` as
  `["null","integer"]` while the fixed tag discovers it as `number` with
  `airbyte_type: integer`. A paired `--reset=none` run can reuse the target's
  discovered catalog for the control read and mask the control bug, because
  the crash is driven by the cursor's catalog JSON-schema type. Fixture reset
  runs separate sweeps, so each image derives its own catalog.
- **No role coverage.** Do not use DynamoDB Local to claim assume-role, IAM,
  or STS coverage. There is no STS emulator here, and `endpoint` only
  overrides the DynamoDB client endpoint.
- **Do not use real AWS.** This harness is for local testing only and must
  never be used against customer AWS accounts, tables containing customer
  data, or Airbyte Cloud.

## Worked example: integer cursor, airbyte#71171

The historical integer-cursor crash can be proven with the base fixture. The
control image fails with
`IllegalArgumentException: No enum constant
io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.INTEGER`
and emits no records; the fixed image reads all three records and emits
`STATE` with `cursor: "3"`.

Use `--reset=fixture` so the 0.3.11 control and 0.4.0 target each run their
own `discover` and `read`. The versions discover different cursor schemas,
and the crash depends on that schema in the configured catalog.
This command also requires an Airbyte Ops build with the configured-catalog
`exclude_none=True` fix: DynamoDB discovery omits `namespace`, and older Ops
builds serialize that omission as `namespace: null`, which 0.4.0 rejects.

```bash
REPRO_OUT="$HOME/dynamodb-hyd310-evidence/patched-ops-1792531195" \
  poe e2e-local \
  --step-name=integer-cursor-71171 \
  --control-version=0.3.11 \
  --test-version=0.4.0 \
  --reset=fixture \
  --sync-mode=incremental \
  --cursor-field=seq \
  --streams=sample \
  --expect-control=fail \
  --expect-test=pass \
  --min-records=3 \
  --min-states=1 \
  --forbid-match=read:any:JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.INTEGER
```

Verified on 2026-10-20 with the Airbyte Ops null-namespace fix:

| Command | Control (`0.3.11`) | Target (`0.4.0`) |
|---------|---------|---------|
| `SPEC` | PASS | PASS |
| `CHECK` | PASS | PASS |
| `DISCOVER` | PASS | PASS |
| `READ` | FAIL — integer-enum crash, 0 records, 0 states | PASS — 3 records, 1 state (`cursor: "3"`) |

The paired command exited 0: the control reproduced the historical failure,
while the target passed and emitted the expected records and state.

## Teardown

The shared library's default `stop-backend.sh` is idempotent:

```bash
BACKEND_NAME=source-dynamodb-db-backend \
  airbyte-integrations/db-harness-lib/scripts/stop-backend.sh
rm -rf "$REPRO_OUT"
unset REPRO_OUT
```
