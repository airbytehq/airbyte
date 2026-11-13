## Version 1.0.8

[#89632](https://github.com/airbytehq/airbyte/pull/89632) — Bump `sshd-mina` 2.13.2 → 2.20.0 (CVE-2026-77185 and twelve further Apache MINA SSHD advisories), `mina-core` 2.0.27 → 2.0.31 (CVE-2026-41409, CVE-2026-41635, CVE-2026-47065) and `bcprov-jdk18on` 1.78.1 → 1.86 (CVE-2026-8763, CVE-2025-14813, CVE-2026-13506), removing the critical findings Docker Scout reports on every Bulk CDK connector image; no behaviour change expected.
`api` constraints pin `bcpkix-jdk18on` and `bcutil-jdk18on` to 1.86 and `bctls-jdk18on` to 1.86.2 so consumers whose drivers pull the 1.78.x family (snowflake-jdbc) do not end up with bcprov 1.86 next to bcutil 1.78.1, which fails `BouncyCastleProvider` initialisation with `NoSuchFieldError` on `IANAObjectIdentifiers.id_MLDSA44_RSA2048_PSS_SHA256`.

## Version 1.0.7

[#89040](https://github.com/airbytehq/airbyte/pull/89040) — Repo-wide reformat with ktfmt 0.65 (trailing commas on one-per-line parameter and argument lists, blank lines between declarations) and removal of SpotBugs suppressions that 4.10.5 on the K2 compiler no longer needs; no behaviour change.

## Version 1.0.6

[#89031](https://github.com/airbytehq/airbyte/pull/89031) — Kotlin compiler 2.4.21 with K2, KSP 2.3.10, kotlinx-coroutines 1.11.0 and mockk 1.14.11 (lifting the strictly-1.13.13 pin); KSP is now declared per source set (`kspTestFixtures`, `kspIntegrationTest`) because KSP2 no longer applies to every compilation; released alongside extract 1.1.20 and load 1.1.6; no runtime behaviour change.

## Version 1.0.5

[#88992](https://github.com/airbytehq/airbyte/pull/88992) — Bump Micronaut to 4.10.31, Jackson to 2.21.7 (Kotlin runtime 2.1.21), JUnit to 5.14 and SpotBugs to 4.10.5. Remove Dagger and `javax.inject`; the CDK and connectors use `jakarta.inject` only. New `verifyMicronautBeanDefinitions` Gradle task (wired into `check` and before every test task) loads every KSP-generated bean definition so a bean that Micronaut would silently drop fails the build instead.

## Version 1.0.4

Bump Testcontainers to 1.21.4 for Docker API v1.44 negotiation.

## Version 1.0.3

Use AIRBYTE_EDITION env var instead of DEPLOYMENT_MODE for the AIRBYTE_CLOUD_DEPLOYMENT feature flag, matching the platform's current environment variable.

## Version 1.0.2

Improved null handling for array types.

## Version 1.0.1

Bump transitive deps with CVEs in unmaintained json schema lib (mbknor-jackson-jsonschema): upgrade classgraph to 4.8.112 (CVE-2021-47621, XXE) and scala-library to 2.13.9 (CVE-2022-36944, deserialization gadget chain).

## Version 1.0.0

Initial independent release of bulk-cdk-core-base.

This marks the beginning of separate versioning for the base, extract, and load CDK packages.
The base package contains shared foundation code used by both extract (source) and load (destination) connectors.

---

## Historical Entries (Unified Bulk CDK)

The entries below are from the unified bulk CDK before the split into separate packages (base, extract, load).
All changes prior to version 1.0.0 applied to the entire bulk CDK as a single versioned package.

## Version 0.2.1

Revert schema parsing change in `legacy-task-loader` that failed streams when handling empty schemas. Schemas without a `type` field now default to object type again.

## Version 0.2.0

Fully separate `legacy-task-loader` toolkit from `core-load`. Drastically simplify `core-load` by removing legacy abstractions.

## Version 0.1.108

load cdk: DataCoercionSuite tests null character in strings

## Version 0.1.107

base cdk: add utility to start ssh tunnel + return endpoint

## Version 0.1.106

**Load CDK**

* Add `DEFAULT_AIRBYTE_INTERNAL_NAMESPACE` constant to `core-load` table package
* Add README documentation to `legacy-task-loader` and `legacy-task-load-db` toolkits

## Version 0.1.105

load cdk: schema regression tests use .json extension

## Version 0.1.104

**Load CDK**

* Add `legacy-task-loader` toolkit containing CDK 0.1.74 code for connectors not yet migrated to the modern tableSchema API
* Add `useLegacyTaskLoader` option to `airbyteBulkConnector` plugin to automatically include the toolkit and exclude core-load
* Rename `load-db` toolkit to `legacy-task-load-db`
* Revert `load-db` to pre components era (cdk 0.1.52)

## Version 0.1.103

load cdk: add table identifier regression test

## Version 0.1.102

load cdk: add schema regression test

## Version 0.1.101

load cdk: Introduce scope and oauth server uri attributes in iceberg polaris spec

## Version 0.1.100

load cdk: allow override of socket count in dest connectors

## Version 0.1.99

load cdk: Enforce maximum parallelism for final aggregate flushes.

## Version 0.1.98

**Extract CDK**

* Fix a bug causing query limit pull a negative number of rows.

## Version 0.1.97

load cdk: slightly refactor schema mapper suite

## Version 0.1.96

**Extract CDK**

* Allow setting an upper limit for the number of rows pulled in a single query for a sequential partition read.

## Version 0.1.95

load cdk: add schema mapper test suite

## Version 0.1.94

extract cdk: fix trigger table handling of empty change tables

## Version 0.1.93

**Load CDK**

* Add KDoc documentation to core destination interfaces: Aggregate, AggregateFactory and RecordDTO.

## Version 0.1.92

load cdk: datacoercion suite calls ValueCoercer.map

## Version 0.1.91

load cdk: upsert records test uses proper target schema

## Version 0.1.90

load cdk: components tests: data coercion tests cover all data types

## Version 0.1.89

load cdk: components tests: data coercion tests for int+number

## Version 0.1.88

**Load CDK**

* Add CDC_CURSOR_COLUMN_NAME constant.

## Version 0.1.87

**Load CDK**

* Properly call NamespaceMapper before calculating final table names.

## Version 0.1.86

**Load CDK**

* Adds toFinalSchema "escape hatch" for final table schema munging
* Refactored Component test fixtures to require explicit StreamTableSchema creation using TableSchemaFactory

## Version 0.1.85

**Extract CDK**

* Fix CDC partition reader race condition when draining records after debezium shutdown.

## Version 0.1.84

load cdk: Move most DB packages into core. Refactor table schema interface into TableSchemaMapper.

## Version 0.1.83

load cdk: more tests to help guide dependency injection dependency implementations

## Version 0.1.82

load cdk: components tests: more schema evolution testcases

## Version 0.1.81

load cdk: components tests: more coverage on upsert

## Version 0.1.80

**Extract CDK**

* Fix default partition_id value for `CheckpointOnlyPartitionReader`.

## Version 0.1.79

**Extract CDK**

* Support multiple ts precision patterns for ts decoding. Expose `columnMetadataFromResultSet` function in `JdbcMetadataQuerier`.

## Version 0.1.78

load cdk: add basic schema evolution test cases

## Version 0.1.77

**Extract CDK**

* Fix duplicate metadata key in JdbcMetadataQuerier.

## Version 0.1.76

**Load CDK**

* Remove a println from our code generating bad logs

## Version 0.1.75

**Extract CDK**

* Improve handling of debezium engine shutdown.

## Version 0.1.74

load cdk: split up ensureSchemaMatches into smaller functions

## Version 0.1.73

**Load CDK**

* More changes to `IcebergTableSynchronizer` to get BigLake working

## Version 0.1.72

**Extract CDK**

* Fix case sensitivity for table filtering.

## Version 0.1.71

**Load CDK**

* Remove noisy logs.

## Version 0.1.70

**Load CDK**

* Changed: Make getOperation in icebergUtil public

## Version 0.1.69

**Load CDK**

* Changed: Update the IcebergTableSynchronizer to allow for individual update operations commit in preparation for BigLake

## Version 0.1.68

**Load CDK**

* Refactor additional state statistic tracking.

## Version 0.1.67

**Load CDK**

* Fix expectations in basic integration tests related to additional stats.

## Version 0.1.66

**Load CDK**

* Added: Support for reporting of additional stats in destination state messages.
* Changed: Refactor coercer interface to separate out coercion and validation.

## Version 0.1.65

extract cdk: fix bug when getting table metadata that cause timeout

## Version 0.1.64

extract cdk: add table filtering to jdbc connectors

## Version 0.1.63

introduce extract-trigger toolkit for trigger-based CDC

## Version 0.1.62

load cdk: correctly parse empty schemas

## Version 0.1.61

Fix bug related to state messages indexing in the dataflow CDK

## Version 0.1.60

load cdk: extract test-only client

## Version 0.1.59

fix upsert test

## Version 0.1.58

load cdk: log unflushed state diagnostic info
## Version 0.1.57

**Extract CDK**

* **Changed:** Remove unnecesarry metafield decoration from database views streams in CDC mode.

## Version 0.1.56

load cdk: improve component tests

## Version 0.1.55

**Extract CDK**

* **Changed:** Timeout in case of no event comes back from dbz.

## Version 0.1.54

Update temporal type representation for proto format

## Version 0.1.53

**Extract CDK**

* **Changed:** Handle debezium engine shutdown properly with socket.

## Version 0.1.52

**Load CDK**

Refactor database operations interfaces and establish comprehensive TableOperationsSuite component test suite.

## Version 0.1.51

Polaris support in the iceberg configuration.

## Version 0.1.50

Better handle interleaved streams in aggregate publishing.

## Version 0.1.49

**Extract CDK**

* **Changed:** Support nano sec to preserve precision in TimeAccessor.

## Version 0.1.48

**Extract CDK**

* **Changed:** Enable heart beat timeout for CDC sync.

## Version 0.1.47

**Extract CDK**

* **Changed:** Correct encoding of CDC_UPDATED_AT and CDC_DELETED_AT fields in protobuf records.

## Version 0.1.46

Noop: Move stream lifecyle dispatchers to bean factory.

## Version 0.1.45

Noop release. 0.1.44 suspected to have a bad publish.

## Version 0.1.44

Dataflow Load CDK: Set dest stats equal to source stats.

## Version 0.1.43

Dataflow Load CDK: Properly handle interleaved per stream states.

## Version 0.1.42

Dataflow Load CDK: Fixes hang when one of many parallel pipelines fails. Organizes thread pools.

## Version 0.1.41

**Extract CDK**

* **Changed:** Prevent a devision by zero error when a table cannot be partitioned.

## Version 0.1.40

Add gradle task to bump CDK version + add changelog entry

## Version 0.1.39

Minor fixes with stream completion logic + proto conversion in Load CDK.

* **Changed:** Minor fixes with stream completion logic + proto conversion

## Version 0.1.38

Adds stats support for "speed" mode to the Load CDK

## Version 0.1.37

load-s3: S3Client forces path-style access, to enable minio compatibility

## Version 0.1.36

Use dedicated dispatcher for parse+aggregate stage for an individual pipeline + cache column name lookup

## Version 0.1.35

Fix input stream wiring for dockerized acceptance tests

## Version 0.1.34

Moved version declaration from build.gradle to version.properties

## Version 0.1.33

Load CDK: Low-code API destination support for dynamically defined discover objects and operations

## Version 0.1.32

Fix input stream wiring for non-dockerized acceptance tests in Load CDK.

## Version 0.1.31

Extract CDK: Pass WhereNode to FromSample node so we can apply filters to the sample query.

## Version 0.1.30

Add Low-code API destination support for statically defined discover operations

## Version 0.1.29

Load CDK: Use correct field name for generation ID meta column.

## Version 0.1.28

Extract CDK: Protobuf encoding fixes to make various types compatible with load(destination) decoding.

## Version 0.1.27

Allow per-test properties for spec integration test

## Version 0.1.26

Improve load-azure-blob-storage documentation.

## Version 0.1.25

Adds proto support to dataflow. Misc transform package cleanup (developer-facing).

## Version 0.1.24

Adds byte counts to emitted state stats.

## Version 0.1.23

Dataflow CDK fails syncs if there are unflushed states at the end of a sync.

## Version 0.1.22

Add EntraID support to azure-blob-storage.

## Version 0.1.21

Adds basic socket support.

## Version 0.1.20

Fix hard failure edge case in stream initialization for in dataflow cdk lifecycle.

## Version 0.1.18

Update load dataflow package accounts for stream completes and dest stats.

## Version 0.1.17

Run aggregate and flush steps on different dispatchers (default and IO respectively).

## Version 0.1.16

Load CDK: Ensure sequential state emission. Remove flushed state/partition keys.

## Version 0.1.15

Extract CDK logs DB version during Check for all JDBC databases.

## Version 0.1.14

Add agent to Load CDK

## Version 0.1.13

Load CDK: Make the resources being used by the dataflow CDK configurable.

## Version 0.1.12

Load CDK: Add teardown to the dataflow pipeline.

## Version 0.1.11

Add finalization to the dataflow pipeline in Load CDK

## Version 0.1.10

Update the version change check to avoid using deprecated libs.

## Version 0.1.7

Update the log4j to allow us to dynamically set the log level via an env variable

## Version 0.1.6

Load CDK: Add the dataflow pipeline. It is a more comprehensive way to write the ingestion pipeline steps. The new pipeline isn't ready to be use in this version.

## Version 0.1.4

Extract CDK fixes for CDC in socket mode - state, partitioning and full refresh streams.

## Version 0.1.3

## Version 0.1.2

## Version 0.1.1

## Version 0.1.0

Adopted Semantic Versioning (SemVer) for the CDK to provide more meaningful version numbers, requiring the CDK version to be set manually in the build.gradle file.
