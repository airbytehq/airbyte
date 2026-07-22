# BigQuery Source Connector - AI Agent Instructions

## Architecture Overview

This is an Airbyte source connector for Google BigQuery, built on the **Airbyte CDK for Java** (v0.13.2). It extends `AbstractDbSource` and uses `BigQueryDatabase` from the CDK to query BigQuery tables and sync them to Airbyte destinations.

**Key Components:**
- [BigQuerySource.java](../src/main/java/io/airbyte/integrations/source/bigquery/BigQuerySource.java): Main connector class extending `AbstractDbSource<StandardSQLTypeName, BigQueryDatabase>`
- [spec.json](../src/main/resources/spec.json): Connection specification defining `project_id`, `dataset_id` (optional), and `credentials_json`
- CDK handles: authentication, query execution, type conversion, incremental syncs, and catalog discovery

## Critical Patterns

### Dataset ID is Optional
The `dataset_id` config parameter is **optional but performance-critical**:
- When set: connector discovers tables from only that dataset (faster schema discovery)
- When null/missing: connector discovers ALL tables across the entire GCP project

Always check for null/empty dataset_id using helper methods:
```java
private boolean isDatasetConfigured(final SqlDatabase database) {
    final JsonNode config = database.getSourceConfig();
    return config.hasNonNull(CONFIG_DATASET_ID) ? !config.get(CONFIG_DATASET_ID).asText().isEmpty() : false;
}
```

### Type Conversion Special Cases
In [discoverInternal](../src/main/java/io/airbyte/integrations/source/bigquery/BigQuerySource.java#L119-L145), STRUCT fields with REPEATED mode are converted to ARRAY type:
```java
if (f.getType().getStandardType() == StandardSQLTypeName.STRUCT && f.getMode() == Field.Mode.REPEATED) {
    standardType = StandardSQLTypeName.ARRAY;
}
```

### Incremental Sync Implementation
Uses parameterized queries for incremental syncs (see [queryTableIncremental](../src/main/java/io/airbyte/integrations/source/bigquery/BigQuerySource.java#L154-L165)):
```java
SELECT %s FROM %s WHERE %s > ?
```
Note: `isCursorType()` returns `true` for ALL types (all BigQuery types support cursor-based incremental).

## Developer Workflows

### Build & Test
```bash
# Build connector
./gradlew :airbyte-integrations:connectors:source-bigquery:build

# Run unit tests (no credentials needed)
./gradlew :airbyte-integrations:connectors:source-bigquery:test

# Run integration tests (requires secrets/credentials.json)
./gradlew :airbyte-integrations:connectors:source-bigquery:integrationTest
```

### Secrets Setup
Integration tests require `secrets/credentials.json` at project root:
- **Airbyte employees**: Get from Rippling under "BigQuery Integration Test User"
- **Contributors**: Create GCP service account with `BigQuery Data Editor` + `BigQuery User` roles

See [README.md](../README.md) for detailed setup instructions.

### Testing Conventions
- **Unit tests** ([BigQuerySourceTest.java](../src/test/java/io/airbyte/integrations/source/bigquery/BigQuerySourceTest.java)): Focus on config validation (empty/null/missing dataset_id cases)
- **Integration tests**: Extend [AbstractBigQuerySourceTest.java](../src/test-integration/java/io/airbyte/integrations/source/bigquery/AbstractBigQuerySourceTest.java) which:
  - Creates temp dataset with random suffix (`airbyte_tests_xxxxxxxx`)
  - Provides `createTable()` and `getConfiguredCatalog()` hooks
  - Auto-cleans dataset in `@AfterEach`
- **Python acceptance tests**: Uses `connector_acceptance_test.plugin` pytest plugin

## Integration Points

### CDK Dependencies
- `BigQueryDatabase`: Handles BigQuery client, query execution, connection validation
- `BigQuerySourceOperations`: Converts BigQuery types to Airbyte types, generates `QueryParameterValue` for cursors
- `AbstractDbSource`: Provides framework for discover, check, read operations
- Feature flag: `features = ['db-sources']` in [build.gradle](../build.gradle#L9)

### External APIs
- Google Cloud BigQuery SDK (`com.google.cloud:google-cloud-bigquery:2.23.2`)
- Authentication via service account JSON credentials

## Common Gotchas

- Quote strings: Use backticks (`` ` ``) for BigQuery identifiers, not single quotes
- No primary keys: BigQuery has no PK concept - `discoverPrimaryKeys()` returns empty map
- STRUCT vs ARRAY: Watch for REPEATED STRUCT fields (they become ARRAY type in Airbyte)
- JVM args in [build.gradle](../build.gradle#L23): `-XX:+ExitOnOutOfMemoryError -XX:MaxRAMPercentage=75.0` for memory safety

## Metadata
- Connector ID: `bfd1ddf8-ae8a-4620-b1d7-55597d2ba08c`
- Release stage: `alpha`, Support level: `community`
- Base image: `docker.io/airbyte/java-connector-base:2.0.0`
- Language: Java (see [metadata.yaml](../metadata.yaml))
