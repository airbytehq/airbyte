# Contributing to source-bigquery-v2

`source-bigquery-v2` is a Bulk CDK (`airbyte-cdk/bulk`, `extract` core + `extract-jdbc` toolkit,
`cdkVersion=1.1.11`) rewrite of the legacy `source-bigquery` connector (0.4.5, old Java CDK, native
`google-cloud-bigquery` client). It connects through Google's Apache-2.0 JDBC driver
(`com.google.cloud:google-cloud-bigquery-jdbc:1.4.0`) and discovers schemas through the native
`google-cloud-bigquery` 2.71.0 client built from the same credentials. The legacy connector is the
parity oracle for `check` and `discover`. Its `spec` properties (`project_id`, `dataset_id`,
`credentials_json`) and `required` list are kept so that saved configurations keep working, but the
spec is laid out like `destination-bigquery`'s (`connection`/`advanced` groups, ordered properties,
titles and descriptions with links) and adds two optional advanced properties: `job_project_id` and
the standard `max_db_connections`.

Stages 1 (`spec` + `check`), 2 (`discover`), 3 (first `read`, stream statuses) and 4 (`read`:
full refresh, cursor-based incremental with resume, legacy state translation, speed mode over Unix
domain sockets in JSONL or protobuf) are implemented. Stage 5 (validation at scale) is not.

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
seed it with the native client (`BigQuerySourceSpeedModeReadTest` additionally connects to the
connector's Unix domain sockets, see "Speed mode" below); `BigQuerySourceSpecTest`,
`BigQuerySourceConfigurationFactoryTest`, `BigQueryFieldTypesTest`, `BigQueryValuesTest`,
`BigQueryProtobufEncodingTest` and `BigQuerySelectQueryGeneratorTest` are plain unit tests.

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

`secrets/config.json` is git-ignored. `credentials_json` is the **contents** of a service account
key file as a JSON string (escaped); `dataset_id` is optional (omit it to discover every dataset of
the project), and so are the two advanced properties:

```json
{
  "project_id": "my-gcp-project",
  "dataset_id": "my_dataset",
  "credentials_json": "{\"type\":\"service_account\",\"project_id\":\"my-gcp-project\",\"private_key_id\":\"...\",\"private_key\":\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n\",\"client_email\":\"airbyte@my-gcp-project.iam.gserviceaccount.com\",\"client_id\":\"...\",\"token_uri\":\"https://oauth2.googleapis.com/token\"}",
  "job_project_id": "my-billing-project",
  "max_db_connections": 4
}
```

- `job_project_id` ("Job Execution Project ID"): the project that runs, and is billed for, the query
  jobs; defaults to `project_id`. It becomes the JDBC driver's `ProjectId` and the native client's
  default project, while every generated query references tables as
  `` `project_id`.`dataset`.`table` `` and every metadata call names `project_id` explicitly. The
  service account needs the BigQuery Job User role on the job project and data access on the data
  project.
- `max_db_connections` ("Max Concurrent Queries to Database"): caps the number of BigQuery query
  jobs running at the same time (`maxConcurrency` of the Bulk CDK, one job per partition reader).
  When unset the connector runs one query at a time on STDIO and one per socket in speed mode.

The key must be a service account key (`"type": "service_account"` with `client_email` and a
PEM-encoded PKCS#8 `private_key`); anything else fails fast in `BigQuerySourceConfigurationFactory`
with a precise `ConfigErrorException`. The JDBC URL is
`jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=<project>;OAuthType=0` and
the credentials travel as the JDBC properties `OAuthServiceAcctEmail` (= `client_email`) and
`OAuthPvtKey` (= the PEM `private_key`), which is what Google's driver expects for `OAuthType=0`
(besides `OAuthPvtKeyPath`, a key _file_); passing the whole key JSON inline is rejected with
"No valid credentials provided." The CDK logs the URL, never the properties.

## Speed mode (socket data channel)

`metadata.yaml` declares `connectorIPCOptions.dataChannel` with `SOCKET`/`STDIO` transports and
`JSONL`/`PROTOBUF` serializations, so the platform may run `read` in speed mode: records, and a
copy of every state, go straight to the destination over Unix domain sockets while logs, traces
and states also go to stdout as usual. The platform configures it with environment variables,
which `application.yml` maps to the `airbyte.connector.data-channel.*` Micronaut properties:

- `DATA_CHANNEL_MEDIUM`: `STDIO` (default) or `SOCKET`;
- `DATA_CHANNEL_FORMAT`: `JSONL` (default) or `PROTOBUF` (records and states on the sockets only;
  stdout stays JSON);
- `DATA_CHANNEL_SOCKET_PATHS`: comma-separated socket file paths, e.g.
  `/tmp/sockets/socket-1.sock,/tmp/sockets/socket-2.sock`. The connector creates and listens on
  every path; the destination connects.

```bash
docker run --rm -e DATA_CHANNEL_MEDIUM=SOCKET -e DATA_CHANNEL_FORMAT=PROTOBUF \
  -e DATA_CHANNEL_SOCKET_PATHS=/tmp/sockets/socket-1.sock,/tmp/sockets/socket-2.sock \
  -v $PWD/secrets:/secrets -v bq-sockets:/tmp/sockets airbyte/source-bigquery-v2:dev \
  read --config /secrets/config.json --catalog /secrets/catalog.json
```

(the sockets must live on a volume another container can mount; Unix domain sockets do not work
across a Docker Desktop bind mount). The log shows `Read configured with data channel medium:
SOCKET. data channel format: PROTOBUF`, and the partition readers wait until a client has
connected to a socket.

What is connector-specific:

- **Concurrency**: `BigQuerySourceConfigurationFactory` sets `maxConcurrency` to `max_db_connections`
  when the user set it, otherwise to 1 on `STDIO` and to the number of socket paths on `SOCKET`, so
  that by default every socket is fed by one BigQuery query at a time.
- **Protobuf values**: the CDK encodes each native column value by the field's Airbyte type. The
  `extract-jdbc` scalar types and the text-parsed `BigQueryDateFieldType`/`BigQueryDateTimeFieldType`/
  `BigQueryTimeFieldType` (`LocalDate`/`LocalDateTime`/`LocalTime`, so dates before 1582 and
  microseconds survive) are encoded natively; `STRUCT` and `ARRAY` columns hold a `JsonNode` and
  their `JsonNodeCodec` is a `ProtobufAwareCustomConnectorJsonCodec` that serializes the node, which
  is how the CDK expects `object`/`array` fields on the wire. In protobuf records the fields have no
  names: they are in alphabetical order of the catalog's `properties`, so the READ-time catalog
  validation dropping a column would misalign the destination (`StateManagerFactory.toStream`).
- Everything else (socket lifecycle, probe packets, `partition_id`/`id` on records and states,
  routing through `OutputMessageRouter`) is the `extract`/`extract-jdbc` toolkit.

Tests: `BigQueryProtobufEncodingTest` round-trips every field type through the CDK's protobuf
encoder and decoder, including a fixture row compared with its JSON rendering;
`BigQuerySourceSpeedModeReadTest` (`@Isolated`, sets the `airbyte.connector.data-channel.*` system
properties for the duration of the read) runs the emulator catalog once on STDIO and once over two
sockets in each format, playing the destination, and checks records, states and statuses.

## Read throughput: sequential reads and the Storage Read API

Each stream is read by a single ordered, resumable query (`application.yml` `mode: sequential`).
Splitting one table into concurrent partitions is deliberately not done: on BigQuery there is no
scan-free way to compute balanced boundaries (`TABLESAMPLE SYSTEM` samples storage blocks, so its
boundaries cluster and one partition ends up with almost the whole table), and each partition query
re-reads whole storage blocks, multiplying the bytes billed. Tables are still read in parallel with
each other, bounded by `maxConcurrency`.

Throughput within a single query comes from the **BigQuery Storage Read API** instead, an opt-in
`use_storage_read_api` spec property (default off). When set, the factory adds the driver property
`EnableHighThroughputAPI=1`, and the driver streams query results as Apache Arrow batches over gRPC
rather than paging JSON through REST. Measured on a 5.2M-row / 1.3 GB table, this took a sequential
read from about 15 minutes to about 90 seconds; value fidelity is identical to the REST path across
every type the connector emits.

Two requirements:

- **JVM flag**: Arrow needs `--add-opens=java.base/java.nio=ALL-UNNAMED` on JDK 17+; without it the
  read fails to initialize Arrow. It is baked into `applicationDefaultJvmArgs` in `build.gradle`, so
  the image has it. If you run the connector another way, add it to `JAVA_OPTS`.
- **Permission**: the service account needs the BigQuery Read Session User role
  (`bigquery.readsessions.create`). Storage Read API usage is billed separately from query bytes.

The property is wired only against the real service; the emulator path leaves it off. The driver
falls back to the REST API automatically for small results (fewer than ~10,000 rows or a single
page), so enabling it never hurts small tables.

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
  (`TIMESTAMP` as epoch seconds with microseconds). `TABLESAMPLE` is accepted on views, which
  BigQuery rejects.
- `TO_JSON_STRING` leaves `DATE`/`DATETIME`/`TIMESTAMP`/`TIME` values unquoted (`{"t":08:00:00}`)
  and renders `BOOL` as `0`/`1`; `BigQueryValues.fromJsonText` repairs both so the read tests
  exercise the same `TO_JSON_STRING` path as the real service. `CAST(... AS STRING)` of temporals
  is exact.
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
- `read`: identical record counts and values on 13 existing tables and one view, covering
  `INT64`, `NUMERIC`, `BIGNUMERIC`, `FLOAT64`, `BOOL`, `STRING` (incl. a column named `interval`
  and `STRING(100)`), `DATE`, `DATETIME`, `TIME`, `TIMESTAMP`, `INTERVAL`, `JSON` and
  `ARRAY<STRING>`. The only differences are the deliberate ones: `DATE` is `2023-07-12` (legacy
  `2023-07-12T00:00:00Z`), `DATETIME` is `2025-11-13T05:18:39.531834` (legacy appended `Z` and
  dropped the fraction), `TIME` and `TIMESTAMP` keep microseconds, `JSON` columns are emitted as
  JSON rather than as a string. `INTERVAL` renders identically (`2021-10 10 10:10:10`).
- Incremental: with an `INT64`/`NUMERIC` cursor the state is `{"primary_key":{},"cursors":{"id":3}}`
  (legacy `{"stream_name":...,"cursor_field":["id"],"cursor":"3","cursor_record_count":1}`); with
  a `TIMESTAMP` cursor `{"cursors":{"updated_at":"2026-08-27T17:23:58.000000Z"}}` (legacy
  `"cursor":"2026-08-27T17:23:58Z"`). Resuming v2 from the **legacy** state file emits no records
  in both cases, as the legacy connector would (`WHERE cursor > value`); resuming from its own
  state re-emits the rows sharing the boundary cursor value (Bulk CDK inclusive lower bound).
- Views: BigQuery rejects the sampling query on a view with "TABLESAMPLE SYSTEM can only be
  applied directly to base tables."; with `BigQueryTableTypes` v2 samples the view with plain
  `LIMIT` queries and reads it (1017 rows, same as legacy).
- `check` on a dataset without tables: v2 fails with "Discovered zero tables.", legacy succeeds
  (confirmed on the real service). `discover` on a deleted dataset: both fail with
  `Not found: Dataset <project>:<dataset>` (legacy wraps it in "Something went wrong").
- **Known gap**: the Bulk CDK drops every column whose name starts with `_ab_` at READ time
  (`MetaField.isMetaFieldID`, meant for the CDC meta fields), so `test_parquet`'s
  `_ab_source_file_url` and `_ab_source_file_last_modified` are advertised by `discover` but
  missing from v2 records while legacy emitted them. Tables written by Airbyte destinations
  commonly have such columns; this needs a CDK change (skip only the connector's own meta fields).

- Seeded dataset `source_bigquery_v2_parity` (tables `all_types`, `with_pk`, `no_rows`, view
  `all_types_view`; DDL in the skill's `databases/bigquery/README.md`): primary keys declared with
  `PRIMARY KEY ... NOT ENFORCED` reach `tableConstraints` and v2 advertises them
  (`[["id"]]`, `[["order_id"],["line"]]`, `is_resumable: true`; legacy `[]`). Records of every
  type (`STRUCT` with nested `TIME`, `ARRAY<STRUCT<..., ARRAY<STRUCT>>>`, `BYTES`, `GEOGRAPHY`,
  `JSON`, `INTERVAL`, `NUMERIC(29,9)`/`BIGNUMERIC(76,38)` extremes, NULLs and empty arrays) match
  legacy after the text-based reads above; `TIMESTAMP '0001-01-01'` is emitted correctly by v2
  while legacy shifted it to `0001-01-03`. `RANGE` is emitted as its canonical text
  (`[2020-01-01, 2020-12-31)`, `[UNBOUNDED, ...)`); the **legacy connector crashes** (`NullPointerException`
  in `getAirbyteType`) on any dataset containing a `RANGE` column, because its BigQuery client
  predates the type, so the column was dropped from the fixture for the comparison.

Everything above the emulator also passes on the real service; nothing is emulator-only anymore.

## Stage status and next steps

| Stage                             | Status                                                                                                                                                                                                                                                                                                                                    |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `spec` + `check`               | Done: `BigQuerySourceConfigurationSpecification`, `BigQuerySourceConfiguration(Factory)`, `BigQueryClientFactory`, check queries and exception classifiers in `application.yml`; tests `BigQuerySourceSpecTest`, `BigQuerySourceConfigurationFactoryTest`, `BigQuerySourceCheckTest`                                                      |
| 2. `discover`                     | Done: `BigQuerySourceMetadataQuerier` (native client, prefetch per dataset, `check` fetches one table), `BigQueryFieldTypes` (+ `BigQueryStructFieldType`/`BigQueryArrayFieldType`), `BigQuerySourceOperations.create()` renders nested schemas; snapshots `expected-catalog-single-dataset.json`, `expected-catalog-all-datasets.json`   |
| 3. first `read` (stream statuses) | Done: `read` boots on the toolkit's `JdbcSequentialPartitionsCreatorFactory`/`DefaultJdbcSharedState`; `BigQuerySourceReadTest` checks `STARTED`/`COMPLETE` for populated, empty and view streams and `STARTED`/`INCOMPLETE` + config error for a missing one                                                                             |
| 4. `read`                         | Done: full refresh, cursor incremental with checkpoint and resume, legacy state translation; verified against the real service for scalar types. Speed mode (socket data channel, JSONL and protobuf) tested on the emulator                                                                                                              |
| 5. validation at scale            | Concurrency measured on the real service: parallel partitions help only with balanced boundaries, which `TABLESAMPLE` cannot give, so reads are `mode: sequential`; per-query throughput comes from the opt-in Storage Read API (`use_storage_read_api`, see "Read throughput" above). Terabyte-scale heap/kill-resume checks still to do |

How `read` is put together:

- Partitions, readers, sampling, checkpointing and the emitted state shape are the `extract-jdbc`
  defaults (`DefaultJdbcPartition*`, `DefaultJdbcStreamStateValue`: `{"primary_key": {...},
"cursors": {...}}`). `application.yml` selects `mode: sequential` with sampling, so each stream is
  read by a single ordered, resumable `SELECT` (one BigQuery job per table plus up to three small
  sampling jobs); tables are read in parallel with each other up to `maxConcurrency`. In speed mode
  `maxConcurrency` is the number of sockets (see "Speed mode" above). See "Read throughput" for why
  within-stream partitioning is off and how the Storage Read API supplies per-query throughput.
- `BigQueryJdbcPartitionFactory` (`@Primary`) wraps `DefaultJdbcPartitionFactory` and only steps
  in when the stream's state is in the legacy `source-bigquery` shape
  (`BigQueryLegacyStreamState`): the legacy cursor string is converted to the cursor column's
  typed JSON value (numbers, ISO-8601 temporals, base64 bytes) and the stream resumes with
  `WHERE cursor > <legacy cursor>`; a legacy state whose `cursor_field` does not match the
  configured cursor, or that cannot be interpreted, resets the stream.
- `BigQueryTableTypes` remembers the `TableDefinition.Type` of every table fetched by the
  metadata querier; `BigQuerySourceOperations` only emits `TABLESAMPLE SYSTEM` for base tables and
  samples everything else (views, materialized views, external tables, snapshots) with a plain
  `LIMIT`. Verified on the real service: a view fails with "TABLESAMPLE SYSTEM can only be applied
  directly to base tables.", and a v2 `read` of a real view succeeds through the fallback.
- Three BigQuery types are not read through the driver's `java.sql` objects, because those lose
  information (all verified against the service on 2026-09-14): `TIME` becomes `java.sql.Time`
  (milliseconds at best, BigQuery has microseconds); `DATE`/`DATETIME` go through
  `java.util.Date`, whose Julian calendar shifts dates before 1582-10-15 (`DATE '0001-01-01'`
  comes back as `0001-01-03` from every accessor, `getString` included); a NULL nested `STRUCT`
  becomes a struct of nulls. So the generator selects `DATE`/`DATETIME`/`TIME` columns as
  `CAST(col AS STRING)` (`BigQueryDateFieldType`, `BigQueryDateTimeFieldType`,
  `BigQueryTimeFieldType` parse the canonical text) and `STRUCT`/`ARRAY` columns as
  `TO_JSON_STRING(col)`, which `BigQueryNestedValueGetter`/`BigQueryValues` convert with the
  nested schema: temporals re-encoded with the CDK codecs, `BYTES` kept as base64, nested
  `GEOGRAPHY` (GeoJSON in that rendering) turned back into WKT (`GeoJson.toWkt`), numbers parsed
  as `BigDecimal`. `TIMESTAMP` stays on the driver (`OffsetDateTime`, epoch-based, exact).
  `WHERE`/`ORDER BY` keep the native columns.
- A fourth driver bug, found on the real service on 2026-09-15 (`test_parquet.flag`, then
  `rodi_proto_type_test.purchases.user_id`): every primitive getter of the driver's
  `BigQueryBaseResultSet` (`getBoolean`, `getLong`, `getInt`, `getShort`, `getByte`, `getDouble`,
  `getFloat`) is `getObject` + `BigQueryTypeRegistry.convert(value, Class)` + an unboxing without a
  null check, so a NULL value throws `NullPointerException: Cannot invoke "java.lang.Long.longValue()"
because the return value of "BigQueryTypeRegistry.convert(Object, Class)" is null`. The toolkit's
  `BooleanFieldType`/`LongFieldType`/`DoubleFieldType` call those getters before `wasNull`, and
  `JdbcSelectQuerier` reports the exception as a `SOURCE_RETRIEVAL_ERROR` change on the record (the
  value is null either way; on `purchases`, 1.2M records, exactly the 21 NULL `INT64` values carried
  the change). `BigQueryBooleanFieldType`, `BigQueryLongFieldType` and `BigQueryDoubleFieldType`
  read `BOOL`/`INT64`/`FLOAT64` with `getObject` (`NullSafeGetter`) instead; the object getters
  (`getString`, `getBytes`, `getBigDecimal`, `getObject(int, Class)`) return null and are not
  affected. The emulator fixture's `all_types` table has an all-NULL row (`id = 2`) so that the
  tests read every type's NULL path.

Next: Stage 5 (terabyte-scale table, memory, checkpoint cadence, kill-and-resume, bytes billed vs
legacy), a CDK fix or workaround for `_ab_*` columns, and a breaking-change evaluation of the
deliberate deviations. The user-facing docs page is `docs/integrations/sources/bigquery-v2.md`.

Scaling of `discover` without `dataset_id`: `BigQuerySourceMetadataQuerier` keeps one small
`TableMetadata` (the mapped columns and the primary key) per fetched table, not the full `Table`
object, so memory scales with the catalog. (An earlier version kept every `Table` and reached
1.4 GiB after 31,000 tables on the test project.) Time is the remaining limit: the CDK's
`DiscoverOperation` lists each dataset's tables in turn and the querier lists with the API's
default page size, so on the test project (37,355 datasets on 2026-09-18, mostly one-table CI
leftovers) a whole-project `discover` needed about 9 minutes for `datasets.list` alone and
covered about 1,500 datasets in 40 minutes. A native-client probe with `pageSize(1000)` listed
all datasets in 55 seconds, so larger pages and listing the tables of several datasets
concurrently are the obvious follow-up. A catalog of that many streams is impractical for the
platform regardless, so users of such projects should set `dataset_id`.
