# Destination Redshift v2

This is the Redshift v2 destination connector, built with the Airbyte Bulk CDK using the Direct Load pattern.

## Implementation Status

### Phase 0: Build System Setup ✅ COMPLETE

- ✅ Created `build.gradle.kts` with Bulk CDK configuration
  - Plugin: `airbyte-bulk-connector` with `core = "load"`
  - Toolkits: `load-csv`, `load-aws`
  - Dependencies: Redshift JDBC driver, HikariCP, AWS SDK
- ✅ Created `gradle.properties` with CDK version 1.0.7
- ✅ Created `metadata.yaml` with connector metadata
- ✅ Created main entry point `RedshiftDestination.kt`
- ✅ Verified build compilation works

### Phase 1: Configuration & Specification Layer ✅ COMPLETE

- ✅ Created `RedshiftSpecification.kt` - Configuration specification with backward compatibility
  - All required fields: host, port, database, schema, username, password
  - Optional fields: jdbcUrlParams, uploadingMethod (S3)
  - `S3StagingConfig` data class for S3 staging configuration
  - `RedshiftSpecificationExtension` for supported sync modes
  - Full backward compatibility with `@JsonIgnoreProperties(ignoreUnknown = true)`
  
- ✅ Created `RedshiftConfiguration.kt` - Typed configuration object
  - Data class extending `DestinationConfiguration`
  - Computed properties: `jdbcUrl`, `hasS3Staging`, S3 config accessors
  - `RedshiftConfigurationFactory` (simplified to single method)
  - Clean, minimal configuration surface
  
- ✅ Created `RedshiftBeanFactory.kt` - Micronaut dependency injection
  - `tempTableNameGenerator()` bean
  - `redshiftConfiguration()` bean
  - `emptyRedshiftDataSource()` for spec operation
  - `redshiftDataSource()` with HikariCP connection pooling
  - `aggregatePublishingConfig()` for batch configuration

- ✅ Created `LEARNING_GUIDE.md` - Comprehensive Kotlin tutorial
  - 34 Kotlin lessons with Java comparisons
  - All lessons embedded as comments in the code
  - Perfect for Java developers learning Kotlin!

### Next Steps: Phase 2 - Schema & Type Mapping Layer

Will implement:
- `RedshiftTableSchemaMapper.kt` - Table and column name mapping
- `RedshiftNamingUtils.kt` - Name sanitization utilities
- Type mapping (Airbyte types → Redshift types)

## Building

From the Airbyte repository root:

```bash
./gradlew :airbyte-integrations:connectors:destination-redshift-v2:build
```

## Architecture

This connector follows the Bulk CDK Direct Load pattern:
- Records written directly to typed final tables (no raw tables by default)
- S3 staging with COPY command for efficient data loading
- Micronaut for dependency injection
- HikariCP for connection pooling
- Backward compatible with legacy Redshift destination configs

## References

- Primary reference: `destination-postgres` (same SQL dialect)
- Secondary reference: `destination-snowflake` (S3 staging patterns)
- Plan document: `../destination-redshift/plan.md`
