# MySQL V2 Destination Connector Tests

This directory contains comprehensive component and integration tests for the MySQL v2 destination connector.

## Test Structure

### Component Tests (`component/`)

Component tests validate individual table operations and core database functionality:

- **MysqlTestConfigFactory.kt**: Provides test configuration from secrets file
  - Uses `@Requires(env = ["component"])` to activate only in component test mode
  - Loads configuration from `secrets/config.json`
  - Creates `MysqlConfiguration` and `MysqlSpecification` beans for testing

- **MysqlTestTableOperationsClient.kt**: Implements test utilities for database operations
  - Implements `TestTableOperationsClient` interface
  - Provides `ping()`, `dropNamespace()`, `insertRecords()`, `readTable()`
  - Handles MySQL-specific type conversions (JSON, TIMESTAMP, DECIMAL, etc.)
  - Uses DataSource for direct database access

- **MysqlTableOperationsTest.kt**: Comprehensive table operations test suite
  - Extends `TableOperationsSuite` from CDK
  - Tests all core operations:
    - Database connectivity
    - Namespace creation/deletion
    - Table creation/deletion
    - Record insertion
    - Row counting
    - Generation ID management
    - Table overwriting
    - Table copying
    - Table upserting (for dedupe mode)

### Integration Tests (`integration/`)

Integration tests validate end-to-end functionality with full sync workflows:

- **MysqlTestDataDumper.kt**: Reads data from MySQL for verification
  - Implements `DestinationDataDumper` interface
  - Creates HikariCP DataSource for database connections
  - Extracts records including Airbyte metadata
  - Parses JSON columns properly

- **MysqlTestDestinationCleaner.kt**: Cleans up test artifacts
  - Implements `DestinationCleaner` interface
  - Drops all test namespaces (schemas) matching `test_%` pattern
  - Used between test runs to ensure clean state

- **MysqlBasicFunctionalityIntegrationTest.kt**: Full integration test suite
  - Extends `BasicFunctionalityIntegrationTest` from CDK
  - Tests complete sync workflows:
    - Basic writes
    - Append mode
    - Truncate mode
    - Schema evolution (adding/modifying columns)
    - Dedupe mode (upsert with primary keys)
    - Namespace handling
    - Checkpointing and state management
  - Configures MySQL-specific behavior:
    - Strongly typed with DECIMAL(38,9) for numbers
    - Pass-through for nested objects/arrays (stored as JSON)
    - Hard delete for CDC deletions
    - Incremental data commits
    - Retroactive schema changes

## Running Tests

### Prerequisites

Create a `secrets/config.json` file in the connector root with your MySQL connection details:

```json
{
  "host": "localhost",
  "port": 3306,
  "database": "test_db",
  "username": "test_user",
  "password": "test_password",
  "ssl": false,
  "ssl_mode": "DISABLED",
  "batch_size": 5000
}
```

### Running Component Tests

Component tests focus on table operations and can be run in isolation:

```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --tests "io.airbyte.integrations.destination.mysql_v2.component.*"
```

Or run individual test classes:

```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --tests "io.airbyte.integrations.destination.mysql_v2.component.MysqlTableOperationsTest"
```

### Running Integration Tests

Integration tests run full sync workflows:

```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --tests "io.airbyte.integrations.destination.mysql_v2.integration.*"
```

Or run individual tests:

```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --tests "io.airbyte.integrations.destination.mysql_v2.integration.MysqlBasicFunctionalityIntegrationTest.testAppend"
```

### Running All Tests

```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration
```

## Test Database Setup

The tests require a MySQL database with:

1. **User Permissions**: The test user needs these privileges:
   ```sql
   CREATE USER 'test_user'@'%' IDENTIFIED BY 'test_password';
   GRANT ALL PRIVILEGES ON test_db.* TO 'test_user'@'%';
   GRANT CREATE, DROP ON *.* TO 'test_user'@'%';
   FLUSH PRIVILEGES;
   ```

2. **Database**: Create the test database:
   ```sql
   CREATE DATABASE IF NOT EXISTS test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

### Using Testcontainers (Optional)

For local development, you can use Testcontainers to automatically spin up a MySQL instance:

```kotlin
// Add to MysqlTestConfigFactory.kt if using Testcontainers
@Requires(env = ["component", "testcontainers"])
@Singleton
@Primary
fun testcontainerConfig(): MysqlConfiguration {
    val mysql = MySQLContainer<Nothing>("mysql:8.0").apply {
        withDatabaseName("test_db")
        withUsername("test_user")
        withPassword("test_password")
        start()
    }

    return MysqlConfiguration(
        host = mysql.host,
        port = mysql.firstMappedPort,
        database = "test_db",
        username = "test_user",
        password = "test_password",
        ssl = false,
        sslMode = SslMode.DISABLED,
        jdbcUrlParams = null,
        batchSize = 5000,
    )
}
```

## Test Coverage

The test suite validates:

### Data Types
- Primitives: String, Integer, Number, Boolean
- Temporal: Date, Time (with/without TZ), Timestamp (with/without TZ)
- Complex: JSON (Objects and Arrays)
- Special: NULL values, large numbers, DECIMAL precision

### Operations
- CREATE/DROP namespaces (databases)
- CREATE/DROP tables
- INSERT records with batch operations
- SELECT and verify data
- ALTER table (add/drop/modify columns)
- OVERWRITE tables (replace content)
- COPY tables (duplicate content)
- UPSERT tables (dedupe with primary keys)

### Sync Modes
- Append: Add new records without deleting old ones
- Truncate: Replace all data in each sync
- Dedupe: Upsert based on primary key and cursor

### Edge Cases
- Schema evolution (adding/removing columns)
- Type changes (widening/narrowing)
- NULL vs unset fields
- Large batches (chunking)
- Concurrent operations
- Error handling and rollback

## CI/CD Integration

These tests are designed to run in CI environments:

1. **GitHub Actions**: Tests run automatically on PRs
2. **Secrets Management**: Config loaded from GitHub Secrets in CI
3. **Parallel Execution**: Component tests support concurrent execution
4. **Cleanup**: Automatic cleanup of test namespaces after each run

## Troubleshooting

### Connection Issues
- Verify MySQL is running: `mysql -h localhost -u test_user -p`
- Check firewall rules allow connections on port 3306
- Verify SSL settings match your MySQL configuration

### Permission Errors
- Ensure user has CREATE/DROP privileges on test database
- Ensure user can create new databases for namespace tests

### Test Failures
- Check MySQL logs: `tail -f /var/log/mysql/error.log`
- Enable debug logging: Set `AIRBYTE_LOG_LEVEL=DEBUG`
- Verify test database is clean before running tests

### Performance Issues
- Adjust batch size in config (default 5000)
- Tune HikariCP connection pool settings
- Consider increasing MySQL `max_allowed_packet` for large batches

## References

- [MySQL Connector Documentation](../../../../../../../docs/integrations/destinations/mysql-v2.md)
- [CDK Testing Guide](../../../../../../../../../../airbyte-cdk/bulk/core/load/README.md)
- [TableOperationsSuite](../../../../../../../../../../airbyte-cdk/bulk/core/load/src/testFixtures/kotlin/io/airbyte/cdk/load/component/TableOperationsSuite.kt)
- [BasicFunctionalityIntegrationTest](../../../../../../../../../../airbyte-cdk/bulk/core/load/src/testFixtures/kotlin/io/airbyte/cdk/load/write/BasicFunctionalityIntegrationTest.kt)
