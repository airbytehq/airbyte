# MySQL v2 Destination - Integration Tests

This directory contains integration tests for the MySQL v2 destination connector.

## Test Structure

```
test-integration/
├── component/                           # Component-level tests
│   ├── MysqlTestConfigFactory.kt       # Test configuration setup
│   ├── MysqlTestTableOperationsClient.kt # Test utilities for database operations
│   └── MysqlTableOperationsTest.kt     # TableOperationsSuite tests
└── integration/                         # Full integration tests
    ├── MysqlTestDataDumper.kt          # Reads data from MySQL for verification
    ├── MysqlTestDestinationCleaner.kt  # Cleans up test artifacts
    └── MysqlBasicFunctionalityIntegrationTest.kt # Full sync tests
```

## Test Types

### Component Tests (`component/`)
Tests individual database operations without running full Airbyte syncs:
- Database connectivity
- Namespace (database) creation/deletion
- Table creation/deletion
- Record insertion
- Row counting
- Generation ID tracking
- Table overwriting (replace content)
- Table copying (duplicate content)
- Table upserting (dedupe with primary key)

### Integration Tests (`integration/`)
Tests full end-to-end Airbyte sync scenarios:
- Basic write operations
- Mid-sync checkpointing and state management
- Namespace handling
- Append mode (incremental sync)
- Truncate mode (full refresh/overwrite)
- Append with schema evolution (add/drop columns)
- Dedupe mode (upsert based on primary key)

## Prerequisites

### MySQL Database
You need a MySQL 5.7+ or 8.0+ database instance for testing. You can use:
- Local MySQL installation
- Docker container: `docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8.0`
- MySQL in CI environment
- Testcontainers (optional, see below)

### User Permissions
The test user needs the following permissions:
```sql
-- Create test user
CREATE USER 'test_user'@'%' IDENTIFIED BY 'test_password';

-- Create test database
CREATE DATABASE test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant permissions
GRANT ALL PRIVILEGES ON test_db.* TO 'test_user'@'%';
GRANT CREATE, DROP ON *.* TO 'test_user'@'%';  -- For namespace operations
FLUSH PRIVILEGES;
```

Required permissions:
- `CREATE` - Create databases and tables
- `DROP` - Drop tables and databases
- `SELECT` - Read data for verification
- `INSERT` - Insert test data
- `UPDATE` - Update data (for dedupe mode)
- `DELETE` - Delete data (for dedupe mode)
- `ALTER` - Modify table schema (for schema evolution)

## Configuration

### secrets/config.json
Create a `secrets/config.json` file with your MySQL connection details:

```bash
cd airbyte-integrations/connectors/destination-mysql-v2
cp secrets/config.json.example secrets/config.json
# Edit secrets/config.json with your credentials
```

Example configuration:
```json
{
  "host": "localhost",
  "port": 3306,
  "database": "test_db",
  "username": "test_user",
  "password": "test_password",
  "ssl": false,
  "ssl_mode": "PREFERRED",
  "jdbc_url_params": null,
  "batch_size": 5000
}
```

**Note**: `secrets/config.json` is gitignored to prevent credential leaks.

### Environment Variables (Alternative)
Instead of `secrets/config.json`, you can set environment variables:
```bash
export MYSQL_TEST_HOST=localhost
export MYSQL_TEST_PORT=3306
export MYSQL_TEST_DATABASE=test_db
export MYSQL_TEST_USERNAME=test_user
export MYSQL_TEST_PASSWORD=test_password
```

## Running Tests

### All Integration Tests
```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration
```

### Component Tests Only
```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --tests "io.airbyte.integrations.destination.mysql_v2.component.*"
```

### Integration Tests Only
```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --tests "io.airbyte.integrations.destination.mysql_v2.integration.*"
```

### Individual Test
```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --tests "io.airbyte.integrations.destination.mysql_v2.component.MysqlTableOperationsTest.testConnectToDatabase"
```

### With Debug Logging
```bash
./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration \
  --info --stacktrace
```

## Testcontainers (Optional)

To use Testcontainers for automatic MySQL setup, uncomment the Testcontainers code in `MysqlTestConfigFactory.kt`:

```kotlin
@Singleton
@Primary
@Requires(env = ["component"])
fun testContainer(): MySQLContainer<*> {
    val container = MySQLContainer("mysql:8.0")
        .withDatabaseName("test_db")
        .withUsername("test_user")
        .withPassword("test_password")
    container.start()
    return container
}

@Singleton
@Primary
fun testConfig(container: MySQLContainer<*>): MysqlConfiguration {
    return MysqlConfiguration(
        host = container.host,
        port = container.firstMappedPort,
        database = container.databaseName,
        username = container.username,
        password = container.password,
        ssl = false,
        sslMode = SslMode.DISABLED,
        jdbcUrlParams = null,
        batchSize = 5000
    )
}
```

Add Testcontainers dependency to `build.gradle.kts`:
```kotlin
testImplementation("org.testcontainers:mysql:1.19.3")
testImplementation("org.testcontainers:testcontainers:1.19.3")
```

## Test Coverage

### Data Types Tested
- Primitives: String, Integer, Number, Boolean, NULL
- Temporal: Date, Time, Timestamp (with/without timezone), Datetime
- Complex: JSON (Objects and Arrays)
- Special: Large numbers, DECIMAL precision

### Sync Modes Tested
- **Append**: Incremental sync without deduplication
- **Dedupe**: Incremental sync with primary key deduplication
- **Overwrite**: Full refresh that replaces all data

### Schema Evolution
- Adding new columns
- Dropping existing columns
- Modifying column types
- Handling nullable changes

### CDC (Change Data Capture)
- Hard delete mode (actually delete records)
- Soft delete mode (keep tombstone records)

## Troubleshooting

### Tests fail with "Access denied"
- Check your MySQL user has all required permissions
- Verify username and password in `secrets/config.json`
- Ensure MySQL server is running and accessible

### Tests fail with "Unknown database"
- Create the test database manually: `CREATE DATABASE test_db;`
- Grant CREATE privilege to test user for dynamic database creation

### Tests fail with "Connection refused"
- Check MySQL server is running: `mysql -u test_user -p`
- Verify host and port in configuration
- Check firewall rules if using remote MySQL

### Tests hang or timeout
- Increase timeout in test configuration
- Check MySQL server performance and resources
- Reduce batch size if memory issues

### Tests fail with "Table already exists"
- Run cleanup: `DROP DATABASE IF EXISTS test_db; CREATE DATABASE test_db;`
- Check previous tests completed successfully
- Ensure test cleaner is running properly

## CI/CD Integration

For CI/CD pipelines, you can:

1. **Use MySQL service container** (GitHub Actions example):
```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: test_db
      MYSQL_USER: test_user
      MYSQL_PASSWORD: test_password
    ports:
      - 3306:3306
    options: >-
      --health-cmd="mysqladmin ping"
      --health-interval=10s
      --health-timeout=5s
      --health-retries=3
```

2. **Set secrets as environment variables**:
```yaml
env:
  MYSQL_TEST_HOST: localhost
  MYSQL_TEST_PORT: 3306
  MYSQL_TEST_DATABASE: test_db
  MYSQL_TEST_USERNAME: test_user
  MYSQL_TEST_PASSWORD: test_password
```

3. **Run tests**:
```yaml
- name: Run integration tests
  run: ./gradlew :airbyte-integrations:connectors:destination-mysql-v2:testIntegration
```

## Contributing

When adding new tests:
- Follow existing patterns from Snowflake/ClickHouse connectors
- Use descriptive test names
- Include both happy path and edge cases
- Clean up test data properly
- Document any special setup requirements
