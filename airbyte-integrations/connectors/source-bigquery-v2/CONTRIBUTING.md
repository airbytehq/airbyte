# Contributing to source-bigquery-v2

`source-bigquery-v2` is a Bulk CDK (`airbyte-cdk/bulk`, `extract` core + `extract-jdbc` toolkit,
`cdkVersion=1.1.11`) rewrite of the legacy `source-bigquery` connector (0.4.5, old Java CDK, native
`google-cloud-bigquery` client). It connects through Google's Apache-2.0 JDBC driver
(`com.google.cloud:google-cloud-bigquery-jdbc:1.4.0`) and discovers schemas through the native
`google-cloud-bigquery` 2.67.0 client built from the same credentials. The legacy connector is the
parity oracle for `spec`, `check` and `discover`; saved configurations must keep working unchanged.

Only Stages 1 (`spec` + `check`) and 2 (`discover`) are implemented. `read` is not.

## Build and test

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home   # macOS/Homebrew; JDK 21
./gradlew :airbyte-integrations:connectors:source-bigquery-v2:compileKotlin
./gradlew :airbyte-integrations:connectors:source-bigquery-v2:test        # Testcontainers, needs Docker
./gradlew :airbyte-integrations:connectors:source-bigquery-v2:assemble    # builds airbyte/source-bigquery-v2:dev
```

The tests never reach Google: `BigQuerySourceCheckTest` and `BigQuerySourceDiscoverTest` start
`ghcr.io/goccy/bigquery-emulator:0.8.1` once through Testcontainers (`BigQueryEmulatorTestFixture`,
`org.testcontainers:gcloud:1.21.4` `BigQueryEmulatorContainer`) and seed it with the native client;
`BigQuerySourceSpecTest`, `BigQuerySourceConfigurationFactoryTest`, `BigQueryFieldTypesTest` and
`BigQuerySelectQueryGeneratorTest` are plain unit tests.

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

The key must be a service account key (`"type": "service_account"` with `client_email` and
`private_key`); anything else fails fast in `BigQuerySourceConfigurationFactory` with a precise
`ConfigErrorException`. The JDBC URL is
`jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=<project>;OAuthType=0` and the
key travels as the `OAuthPvtKey` JDBC property (the CDK logs the URL, never the properties).

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

Still to be checked against a real BigQuery project (no credentials yet; the legacy image has no
emulator setting, so nothing above has been diffed image-to-image):

- `discover` on the same project with `airbyte/source-bigquery:0.4.5` and the `dev` image, diffed
  with the skill's `parity/diff-catalogs.py` (which labels the deliberate differences above).
- Primary keys declared by DDL (`PRIMARY KEY (...) NOT ENFORCED`) reaching `tableConstraints`.
- The messages of real authentication and permission failures, and the
  `airbyte.connector.exception-classifiers` rules in `application.yml` that classify them (the
  `input-example`s were written from documentation, not captured).
- `REQUIRED` modes, `numRows`, `INFORMATION_SCHEMA` and the Google JDBC driver's `getColumns`
  output against the real service.

## Stage status and next steps

| Stage | Status |
|---|---|
| 1. `spec` + `check` | Done: `BigQuerySourceConfigurationSpecification`, `BigQuerySourceConfiguration(Factory)`, `BigQueryClientFactory`, check queries and exception classifiers in `application.yml`; tests `BigQuerySourceSpecTest`, `BigQuerySourceConfigurationFactoryTest`, `BigQuerySourceCheckTest` |
| 2. `discover` | Done: `BigQuerySourceMetadataQuerier` (native client, prefetch per dataset, `check` fetches one table), `BigQueryFieldTypes` (+ `BigQueryStructFieldType`/`BigQueryArrayFieldType`), `BigQuerySourceOperations.create()` renders nested schemas; snapshots `expected-catalog-single-dataset.json`, `expected-catalog-all-datasets.json` |
| 3. first `read` (stream statuses) | To do |
| 4. `read` | To do |

Stage 3: with `extract-jdbc` the `PartitionsCreatorFactory`, `JdbcPartitionsCreator` and
`JdbcPartitionReader` are provided; the connector must supply a `JdbcPartitionFactory` bean with its
partition and stream-state classes (start from the toolkit's `DefaultJdbcPartition*`), so that
`read` boots, runs one partition per stream and emits `STARTED`/`COMPLETE`. The
`MetaFieldDecorator` no-op already exists (`BigQuerySourceOperations.decorateRecordData`).
Gate: an in-process `read` against the emulator (populated table, `no_rows`, a missing table) and
`docker run ... read` with the same configured catalog.

Stage 4: `BigQuerySourceOperations` already renders GoogleSQL for the CDK query AST (backtick
quoting, `dataset.table` relative to the connection project, literal `LIMIT`, `TABLESAMPLE SYSTEM
(<pct> PERCENT)` inside a subquery, `?` bindings, `SELECT MAX(cursor)`), unit-tested in
`BigQuerySelectQueryGeneratorTest` but never executed. Open questions, all to be verified against
the driver: `STRUCT`/`ARRAY` values arriving as `java.sql.Struct`/`java.sql.Array` and their
conversion in `BigQueryJsonValueGetter` (struct attributes are currently keyed by position, not
field name); `TIMESTAMP` through `getObject(idx, OffsetDateTime::class.java)`
(`OffsetDateTimeFieldType`); `DATETIME`/`TIME`/`DATE` accessors; `NUMERIC`/`BIGNUMERIC` precision;
whether `TABLESAMPLE` is legal on views; driver knobs `EnableHighThroughputAPI` (Storage Read API,
off by default), `MaximumBytesBilled`, `JobCreationMode`; cursor-based incremental with the same
state shape the legacy connector persisted (capture it from the legacy image first); record parity
with legacy `BigQuerySourceOperations.rowToJson` (`DATE`/`DATETIME`/`TIMESTAMP` rendered as ISO-8601,
`BYTES` base64, nested records by index).
