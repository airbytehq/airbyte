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
