# Contributing to source-bigquery-v2

`source-bigquery-v2` is a Bulk CDK (`airbyte-cdk/bulk`, `extract` core + `extract-jdbc` toolkit,
`cdkVersion=1.1.11`) rewrite of the legacy `source-bigquery` connector (0.4.5, old Java CDK, native
`google-cloud-bigquery` client). It connects through Google's Apache-2.0 JDBC driver
(`com.google.cloud:google-cloud-bigquery-jdbc:1.4.0`) and discovers schemas through the native
`google-cloud-bigquery` 2.67.0 client built from the same credentials. The legacy connector is the
parity oracle for `spec`, `check` and `discover`; saved configurations must keep working unchanged.

Stages 1 (`spec` + `check`), 2 (`discover`), 3 (first `read`, stream statuses) and 4 (`read`:
full refresh, cursor-based incremental with resume, legacy state translation) are implemented.
Stage 5 (validation at scale) is not.

## Build and test

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home   # macOS/Homebrew; JDK 21
./gradlew :airbyte-integrations:connectors:source-bigquery-v2:compileKotlin
./gradlew :airbyte-integrations:connectors:source-bigquery-v2:test        # Testcontainers, needs Docker
./gradlew :airbyte-integrations:connectors:source-bigquery-v2:assemble    # builds airbyte/source-bigquery-v2:dev
```

The tests never reach Google: `BigQuerySourceCheckTest`, `BigQuerySourceDiscoverTest` and
`BigQuerySourceReadTest` start `ghcr.io/goccy/bigquery-emulator:0.8.1` once through Testcontainers
(`BigQueryEmulatorTestFixture`, `org.testcontainers:gcloud:1.21.4` `BigQueryEmulatorContainer`) and
seed it with the native client; `BigQuerySourceSpecTest`, `BigQuerySourceConfigurationFactoryTest`,
`BigQueryFieldTypesTest` and `BigQuerySelectQueryGeneratorTest` are plain unit tests.

There is no `spotlessApply` task for connectors. Format with the ktfmt version CI uses:

```bash
curl -sSfL -o /tmp/ktfmt-0.39.jar https://repo1.maven.org/maven2/com/facebook/ktfmt/0.39/ktfmt-0.39-jar-with-dependencies.jar
find airbyte-integrations/connectors/source-bigquery-v2/src -name '*.kt' | xargs java -jar /tmp/ktfmt-0.39.jar --kotlinlang-style
```

## Running the connector locally

```bash
docker run --rm airbyte/source-bigquery-v2:dev spec
docker run --rm -v $PWD/secrets:/secrets airbyte/source-bigquery-v2:dev check    --config /secrets/config.json
docker run --rm -v $PWD/secrets:/secrets airbyte/source-bigquery-v2:dev discover --config /secrets/config.json
```

`secrets/config.json` is git-ignored. The properties are the legacy ones; `credentials_json` is the
**contents** of a service account key file as a JSON string (escaped), and `dataset_id` is optional
(omit it to discover every dataset of the project):

```json
{
  "project_id": "my-gcp-project",
  "dataset_id": "my_dataset",
  "credentials_json": "{\"type\":\"service_account\",\"project_id\":\"my-gcp-project\",\"private_key_id\":\"...\",\"private_key\":\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n\",\"client_email\":\"airbyte@my-gcp-project.iam.gserviceaccount.com\",\"client_id\":\"...\",\"token_uri\":\"https://oauth2.googleapis.com/token\"}"
}
```

The key must be a service account key (`"type": "service_account"` with `client_email` and a
PEM-encoded PKCS#8 `private_key`); anything else fails fast in `BigQuerySourceConfigurationFactory`
with a precise `ConfigErrorException`. The JDBC URL is
`jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=<project>;OAuthType=0` and
the credentials travel as the JDBC properties `OAuthServiceAcctEmail` (= `client_email`) and
`OAuthPvtKey` (= the PEM `private_key`), which is what Google's driver expects for `OAuthType=0`
(besides `OAuthPvtKeyPath`, a key *file*); passing the whole key JSON inline is rejected with
"No valid credentials provided." The CDK logs the URL, never the properties.

## The BigQuery emulator

`ghcr.io/goccy/bigquery-emulator` is a community project (MIT, beta) that serves the BigQuery REST
API on port 9050 and the Storage API on 9060 without authentication. The connector is pointed at it
with the `BIGQUERY_EMULATOR_HOST` environment variable (the convention of Google's Go/Python
clients) or the `airbyte.source.bigquery.emulator-host` system property (`BigQueryEmulator` in
`BigQuerySourceConfiguration.kt`). In that mode:

- the native client uses `BigQueryOptions.setHost(<emulator>)` with `NoCredentials`;
- the JDBC URL becomes `jdbc:bigquery://<emulator>;ProjectId=<project>;OAuthType=2` with the
  properties `OAuthAccessToken=emulator` and `EndpointOverrides=BIGQUERY=<emulator>`;
- `credentials_json` must still be non-blank but is not validated. Never set the variable in
  production.

Running the image against a local emulator (the `check`/`discover` parity scripts in the
`new-database-source-connector` skill, `databases/bigquery/parity/`, automate this, including a
`seed.sh` that recreates the test fixture's datasets over REST):

```bash
docker network create bq-v2-net
docker run -d --name bq-emulator --network bq-v2-net -p 9050:9050 -p 9060:9060 \
  ghcr.io/goccy/bigquery-emulator:0.8.1 --project=test-project
# seed it (see the skill's parity/seed.sh), then:
docker run --rm --network bq-v2-net -e BIGQUERY_EMULATOR_HOST=http://bq-emulator:9050 \
  -v $PWD/secrets:/secrets airbyte/source-bigquery-v2:dev discover --config /secrets/config.json
```

with `secrets/config.json` = `{"project_id": "test-project", "dataset_id": "airbyte_test",
"credentials_json": "{\"type\":\"service_account\",\"client_email\":\"x@y\",\"private_key\":\"unused\"}"}`.

Known deviations of emulator 0.8.1 from BigQuery (verified 2026-09-11; see also the emulator's
`docs/feature-support.md`):

- `INFORMATION_SCHEMA` has only `SCHEMATA`, `TABLES`, `TABLE_OPTIONS` and `COLUMNS` (no
  `TABLE_CONSTRAINTS`, `KEY_COLUMN_USAGE`, `COLUMN_FIELD_PATHS`), and `COLUMNS.data_type` reports
  `DOUBLE` for `FLOAT64`.
- `tables.get` returns full nested RECORD/REPEATED schemas but omits `numRows` until the table has
  rows (real BigQuery returns `"0"`), and `NOT NULL` columns of DDL-created tables come back as
  `NULLABLE` (a `tables.insert` with `REQUIRED` modes is echoed back faithfully).
- A DDL `PRIMARY KEY (...) NOT ENFORCED` is dropped; `tableConstraints` sent via `tables.insert` are
  echoed back, which is how `with_pk` gets its primary key in the tests.
- `tables.insert` requires the legacy REST type names (`INTEGER`, `FLOAT`, `BOOLEAN`, `RECORD`);
  the native Java client sends those, hand-written JSON with `INT64`/`STRUCT` is rejected.
- Reserved words (`at`, `by`, `inner`) cannot be nested STRUCT field names in DDL; a `FLOAT64`
  nested inside `ARRAY<STRUCT<...>>` cannot be inserted into (type mismatch FLOAT vs DOUBLE).
- `SELECT 1 WHERE FALSE` fails ("Query without FROM clause cannot have a WHERE clause", which real
  BigQuery also rejects); `SELECT 1 FROM UNNEST([1]) WHERE FALSE` works and is the `check` query.
- `TABLESAMPLE SYSTEM (n PERCENT)`, positional and named parameters and backtick-quoted
  `project.dataset.table` references work; `jobs.query` returns every value as a string
  (`TIMESTAMP` as epoch seconds with microseconds).
- Not-found errors read `dataset X is not found` / `project Y is not found`; real BigQuery says
  `Not found: Dataset p:d`, which is the phrasing the `exception-classifiers` rule targets. `check`
  reports both as a config error regardless, because `CheckOperation` treats any failure that way.
- Requests are not authenticated, so every credentials failure path needs real BigQuery.

## Parity with source-bigquery (legacy)

Identical:

- `connectionSpecification` `properties`, `required`, `title` and `$schema`, and `documentationUrl`
  (`BigQuerySourceSpecTest` compares `expected-spec.json` with `legacy-spec.json`, the `spec`
  output of `airbyte/source-bigquery:0.4.5`). Top-level keys differ: the legacy spec carries
  `supportsIncremental` and `supported_sync_modes`, the Bulk CDK emits `additionalProperties: true`.
- Namespaces are datasets (all datasets of the project when `dataset_id` is blank), streams are the
  tables, views, materialized views, external tables and snapshots of `tables.list`, discovered with
  the same `datasets.list` -> `tables.list` -> `tables.get` calls (legacy: `BigQueryDatabase.
  getProjectTables`/`getDatasetTables`; v2 runs `tables.get` on 32 threads per dataset).
- `INT64` -> `{"type":"number","airbyte_type":"integer"}`, `FLOAT64`/`NUMERIC`/`BIGNUMERIC` ->
  `number`, `BOOL` -> `boolean`, `STRING`/`GEOGRAPHY`/`INTERVAL` -> `string`.

Deliberately different (documented in `BigQueryFieldTypes.kt`; each is a schema change for existing
connections and needs a breaking-change evaluation before release):

- `DATE`, `DATETIME`, `TIMESTAMP`, `TIME` are typed (`format` + `airbyte_type`), `BYTES` is
  `string` with `contentEncoding: base64`, `JSON` is `airbyte_type: json`; legacy declared all of
  them as plain `string`.
- `STRUCT` columns carry nested `properties`, `ARRAY` columns carry `items`; legacy emitted a bare
  `{"type":"object"}` / `{"type":"array"}` and declared a `REPEATED` scalar as the scalar type.
- `source_defined_primary_key` comes from the table's `PRIMARY KEY` constraint (`tableConstraints`)
  and such streams are `is_resumable: true`; legacy never reported primary keys.
- `INCREMENTAL` is advertised only when a column can serve as a cursor (`JdbcAirbyteStreamFactory`
  rule); legacy advertised it on every stream (`isCursorType` returned `true` unconditionally).
- ML models (`TableDefinition.Type.MODEL`) are skipped.
- `credentials_json` must be a service account key; legacy fell back to Application Default
  Credentials when it was blank, and passed any `GoogleCredentials.fromStream` key.
- `check`: legacy ran `select 1` and, with a dataset, `select 1 from `<dataset>`.`INFORMATION_SCHEMA.TABLES` where 1=0`;
  v2 runs discovery (`datasets.list`/`tables.list`/`tables.get`) plus
  `SELECT 1 FROM UNNEST([1]) WHERE FALSE` over JDBC, so a dataset without tables fails with
  "Discovered zero tables." where legacy succeeded (legacy behaviour inferred from its code, not run).

Checked against the `dataline-integration-testing` project on 2026-09-14 with the service account
key of the legacy connector's integration tests (the skill's `parity/run-checks.sh`,
`run-discover.sh`, `run-read.sh`, `diff-catalogs.py` and `diff-records.py`; both images were run with
the same configs, and `read` with configured catalogs derived from each image's own `discover`):

- `check`: both images succeed with and without `dataset_id`. Failure messages differ in wording
  only: unknown dataset -> `Not found: Dataset <project>:<dataset>` in both (legacy appends
  ` was not found in location US`); unknown project -> v2 `Project <id> is not found. Make sure it
  references valid GCP project that hasn't been deleted.`, legacy `ProjectId must be non-empty`;
  broken private key -> v2 `'credentials_json' has an invalid 'private_key'...` (validated in the
  config factory because the driver only says `No valid credentials provided.`), legacy `Unexpected
  exception reading PKCS#8 data`; `authorized_user` JSON -> v2 factory message, legacy `'type' value
  'authorized_user' not recognized`. All are classified `config_error`.
- `discover`: a 50-table dataset written by destination-bigquery differs only by the deliberate
  type upgrades listed above (382 typed `TIMESTAMP`/`DATE` columns, 217 typed `JSON` columns);
  two small tables differ only by `is_resumable: false` and `source_defined_cursor: false`, which
  the legacy connector did not emit at all.
- `read`: same records (`INT64`, `NUMERIC`, `FLOAT64`, `BOOL`, `STRING`, `TIMESTAMP`, `JSON`) for
  `id_and_name` (3 rows), a `NUMERIC`-keyed datatype table (5 rows) and two destination-written
  tables (4 and 11 rows). Differences are the deliberate ones: `TIMESTAMP` keeps microseconds
  (`2025-09-09T12:17:43.462000Z`, legacy `2025-09-09T12:17:43Z`) and `JSON` columns are emitted as
  JSON rather than as a string. The state after an incremental read is
  `{"primary_key":{},"cursors":{"id":3}}` (legacy `{"stream_name":...,"cursor_field":["id"],
  "cursor":"3","cursor_record_count":1}`); resuming v2 from the **legacy** state file emits no
  records, as the legacy connector would (`WHERE id > 3`).
- **Known gap**: the Bulk CDK drops every column whose name starts with `_ab_` at READ time
  (`MetaField.isMetaFieldID`, meant for the CDC meta fields), so `test_parquet`'s
  `_ab_source_file_url` and `_ab_source_file_last_modified` are advertised by `discover` but
  missing from v2 records while legacy emitted them. Tables written by Airbyte destinations
  commonly have such columns; this needs a CDK change (skip only the connector's own meta fields).

Not yet exercised against the real service (needs a seeded dataset; creating one with the shared
key is pending approval): `DATE`, `DATETIME`, `TIME`, `BYTES`, `GEOGRAPHY`, `INTERVAL`, `RANGE`,
`STRUCT`/`ARRAY` values, temporal cursors, `TABLESAMPLE` on views/external tables, primary keys
declared by DDL, and the driver's `getColumns` output. All of these pass on the emulator.

## Stage status and next steps

| Stage | Status |
|---|---|
| 1. `spec` + `check` | Done: `BigQuerySourceConfigurationSpecification`, `BigQuerySourceConfiguration(Factory)`, `BigQueryClientFactory`, check queries and exception classifiers in `application.yml`; tests `BigQuerySourceSpecTest`, `BigQuerySourceConfigurationFactoryTest`, `BigQuerySourceCheckTest` |
| 2. `discover` | Done: `BigQuerySourceMetadataQuerier` (native client, prefetch per dataset, `check` fetches one table), `BigQueryFieldTypes` (+ `BigQueryStructFieldType`/`BigQueryArrayFieldType`), `BigQuerySourceOperations.create()` renders nested schemas; snapshots `expected-catalog-single-dataset.json`, `expected-catalog-all-datasets.json` |
| 3. first `read` (stream statuses) | Done: `read` boots on the toolkit's `JdbcConcurrentPartitionsCreatorFactory`/`DefaultJdbcSharedState`; `BigQuerySourceReadTest` checks `STARTED`/`COMPLETE` for populated, empty and view streams and `STARTED`/`INCOMPLETE` + config error for a missing one |
| 4. `read` | Done: full refresh, cursor incremental with checkpoint and resume, legacy state translation; verified against the real service for scalar types |
| 5. validation at scale | To do |

How `read` is put together:

- Partitions, readers, sampling, checkpointing and the emitted state shape are the `extract-jdbc`
  defaults (`DefaultJdbcPartition*`, `DefaultJdbcStreamStateValue`: `{"primary_key": {...},
  "cursors": {...}}`). `application.yml` selects `mode: concurrent` with sampling; on STDIO
  `maxConcurrency` is 1, so tables below the target partition size are read by a single
  non-resumable `SELECT`, i.e. one BigQuery job per table plus up to three small sampling jobs.
- `BigQueryJdbcPartitionFactory` (`@Primary`) wraps `DefaultJdbcPartitionFactory` and only steps
  in when the stream's state is in the legacy `source-bigquery` shape
  (`BigQueryLegacyStreamState`): the legacy cursor string is converted to the cursor column's
  typed JSON value (numbers, ISO-8601 temporals, base64 bytes) and the stream resumes with
  `WHERE cursor > <legacy cursor>`; a legacy state whose `cursor_field` does not match the
  configured cursor, or that cannot be interpreted, resets the stream.
- `BigQueryTableTypes` remembers the `TableDefinition.Type` of every table fetched by the
  metadata querier; `BigQuerySourceOperations` only emits `TABLESAMPLE SYSTEM` for tables and
  snapshots and samples views, materialized views and external tables with a plain `LIMIT`.
- `STRUCT`/`ARRAY` values arrive from the driver as `java.sql.Struct`/`java.sql.Array`;
  `BigQueryNestedValueGetter`/`BigQueryValues` convert them to JSON using the nested schema
  (struct attributes keyed by field name, nested temporals rendered with the CDK codecs, `JSON`
  strings parsed).

Next: Stage 5 (terabyte-scale table, memory, checkpoint cadence, kill-and-resume, bytes billed vs
legacy), the real-service checks listed above once a dataset can be seeded, a CDK fix or workaround
for `_ab_*` columns, the docs page, and a breaking-change evaluation of the deliberate deviations.
