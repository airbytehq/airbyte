# Troubleshooting: Common Issues and Solutions

**Summary:** Quick reference for debugging common issues when building source connectors.

---

## Build & Startup Errors

### Error: No bean of type [...] exists

**Symptom:**
```
io.micronaut.context.exceptions.NoSuchBeanException: No bean of type [io.airbyte.cdk.discover.MetadataQuerier$Factory] exists
```

**Cause:** Missing `@Singleton` or `@Primary` annotation on your implementation

**Solution:**
```kotlin
@Singleton
@Primary  // Required if CDK has a default implementation
class {DB}SourceMetadataQuerier {
    // ...
}
```

---

### Error: Multiple possible bean candidates

**Symptom:**
```
io.micronaut.context.exceptions.NonUniqueBeanException: Multiple possible bean candidates found
```

**Cause:** Both your implementation and CDK default are registered

**Solution:** Add `@Primary` to your implementation:
```kotlin
@Singleton
@Primary  // This tells Micronaut to use your implementation
class {DB}SourceOperations : JdbcMetadataQuerier.FieldTypeMapper {
```

---

### Error: Failed to inject value for parameter

**Symptom:**
```
Failed to inject value for parameter [dataChannelMedium] of class: ...
```

**Cause:** Missing configuration in `application.yml`

**Solution:** Ensure `application.yml` has required properties:
```yaml
airbyte:
  connector:
    data-channel:
      medium: ${DATA_CHANNEL_MEDIUM:STDIO}
      format: ${DATA_CHANNEL_FORMAT:JSONL}
```

---

### Error: Could not find or load main class

**Symptom:**
```
Error: Could not find or load main class io.airbyte.integrations.source.{db}.{DB}Source
```

**Cause:** Main class name doesn't match `build.gradle` configuration

**Solution:** Ensure `application.mainClass` matches your source file:
```groovy
// build.gradle
application {
    mainClass = 'io.airbyte.integrations.source.{db}.{DB}Source'
}
```

```kotlin
// {DB}Source.kt - must be object, not class
object {DB}Source {
    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteSourceRunner.run(*args)
    }
}
```

---

## Spec Operation Errors

### Error: Spec returns empty properties

**Symptom:** Spec output has no properties in connectionSpecification

**Cause:** Missing Jackson annotations on specification class

**Solution:** Add required annotations:
```kotlin
@JsonSchemaTitle("{Database} Source Spec")
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
class {DB}SourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("host")  // Required for field to appear
    @JsonSchemaTitle("Host")
    lateinit var host: String
}
```

---

### Error: Property marked as required but has default

**Symptom:** Validation fails because required field has default value

**Cause:** Kotlin's default values don't work with `lateinit`

**Solution:**
- Use `lateinit var` for required fields (no default)
- Use `var ... = default` for optional fields

```kotlin
// Required - use lateinit
@JsonProperty("host")
lateinit var host: String

// Optional - use default value
@JsonProperty("port")
var port: Int = 5432
```

---

## Check Operation Errors

### Error: Connection refused

**Symptom:**
```
Connection refused to host: localhost, port: 5432
```

**Cause:** Database not running or wrong host/port

**Solution:**
1. Verify database is running
2. Check host/port in config
3. For Docker: use host.docker.internal or container network

---

### Error: Authentication failed

**Symptom:**
```
password authentication failed for user "testuser"
```

**Cause:** Wrong username/password

**Solution:**
1. Verify credentials in config
2. Check database user exists and has permissions
3. Verify password doesn't need URL encoding

---

## Discover Operation Errors

### Error: No tables found

**Symptom:** Discover returns empty catalog

**Cause:** Namespace configuration doesn't match database

**Solution:** Check `namespace-kind` in `application.yml`:
```yaml
airbyte:
  connector:
    extract:
      jdbc:
        # Options: CATALOG, SCHEMA, CATALOG_AND_SCHEMA
        namespace-kind: SCHEMA  # PostgreSQL: schema.table
        # or
        namespace-kind: CATALOG  # MySQL: database.table
```

---

### Error: Unknown column type

**Symptom:**
```
Column 'custom_col' has unknown type 'CUSTOM_TYPE'
```

**Cause:** Type not handled in `leafType()`

**Solution:** Add type mapping in SourceOperations:
```kotlin
private fun leafType(type: SystemType): JdbcFieldType<*> {
    return when (type.typeName.uppercase()) {
        // ... existing types ...
        "CUSTOM_TYPE" -> StringFieldType  // Map to appropriate type
        else -> PokemonFieldType  // Fallback
    }
}
```

---

## Read Operation Errors

### Error: Column not found

**Symptom:**
```
Column 'updated_at' not found
```

**Cause:** Cursor field doesn't exist or has different name

**Solution:**
1. Verify cursor field exists in table
2. Check for case sensitivity
3. Verify column is included in SELECT

---

### Error: Cannot convert value

**Symptom:**
```
Cannot convert value '2024-01-15' to type LocalDateTime
```

**Cause:** Wrong field type mapping

**Solution:** Fix type mapping in `leafType()`:
```kotlin
"DATE" -> LocalDateFieldType  // Not LocalDateTimeFieldType
"DATETIME" -> LocalDateTimeFieldType
"TIMESTAMP" -> LocalDateTimeFieldType
"TIMESTAMPTZ" -> OffsetDateTimeFieldType
```

---

### Error: State not serializable

**Symptom:**
```
Cannot serialize state value of type OffsetDateTime
```

**Cause:** State contains non-JSON types

**Solution:** Convert to strings in state:
```kotlin
override fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue {
    val cursorValue = lastRecord.get(cursor.id)?.asText()  // Always use asText()
    return Jsons.jsonNode({DB}SourceJdbcStreamStateValue(
        cursors = cursorValue,  // String, not OffsetDateTime
    ))
}
```

---

### Error: Out of memory

**Symptom:**
```
java.lang.OutOfMemoryError: Java heap space
```

**Cause:** Large table loaded into memory

**Solution:** Configure streaming in `application.yml`:
```yaml
airbyte:
  connector:
    extract:
      jdbc:
        default-fetch-size: 1000  # Reduce from default
        memory-capacity-ratio: 0.6
```

---

## State & Resumability Errors

### Error: Cannot resume from state

**Symptom:** Connector restarts from beginning instead of resuming

**Cause:** State format changed or state not parseable

**Solution:**
1. Verify state JSON matches `{DB}SourceJdbcStreamStateValue` class
2. Check field names match `@JsonProperty` annotations
3. Reset state and start fresh if format changed

---

### Error: Duplicate records after resume

**Symptom:** Same records appear multiple times after restart

**Cause:** Cursor not unique or state checkpoint incorrect

**Solutions:**
1. Use higher precision cursor (e.g., `TIMESTAMP(6)`)
2. Ensure state is updated BEFORE emitting
3. Use `isLowerBoundIncluded = false` for cursor queries

---

## SQL Syntax Errors

### Error: Syntax error in generated SQL

**Symptom:**
```
Syntax error at or near "FROM"
```

**Cause:** Wrong identifier quoting for your database

**Solution:** Adjust quoting in `Field.sql()`:
```kotlin
// MySQL: backticks
private fun Field.sql(): String = "`$id`"

// PostgreSQL/SQL Server: double quotes
private fun Field.sql(): String = "\"$id\""

// Oracle: double quotes (uppercase by default)
private fun Field.sql(): String = "\"${id.uppercase()}\""
```

---

## Testing Tips

### Using Testcontainers

```kotlin
@Testcontainers
class {DB}SourceTest {
    companion object {
        @Container
        val container = {DB}Container(DockerImageName.parse("{db}:latest"))
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test")
    }

    @Test
    fun testConnection() {
        val config = mapOf(
            "host" to container.host,
            "port" to container.firstMappedPort,
            "database" to "testdb",
            "username" to "test",
            "password" to "test",
        )
        // Test with config...
    }
}
```

### Debug Logging

Add to `application.yml`:
```yaml
logger:
  levels:
    io.airbyte.integrations.source.{db}: DEBUG
    io.airbyte.cdk: DEBUG
```

### Print Generated SQL

```kotlin
override fun generate(ast: SelectQuerySpec): SelectQuery {
    val sql = ast.sql()
    log.debug { "Generated SQL: $sql" }  // Add logging
    return SelectQuery(sql, ast.select.columns, ast.bindings())
}
```

---

## Quick Fixes Checklist

| Symptom | Check |
|---------|-------|
| Build fails | Package names match? Main class in `build.gradle`? |
| DI errors | `@Singleton` and `@Primary` annotations? |
| Spec empty | `@JsonProperty` annotations? |
| Check fails | Database running? Credentials correct? |
| Discover empty | `namespace-kind` correct? Permissions? |
| Types wrong | `leafType()` mapping correct? |
| State errors | Field names match `@JsonProperty`? |
| Resume fails | State format changed? Reset state. |
| SQL errors | Identifier quoting correct for DB? |
| Memory issues | `fetch-size` configured? |

---

## Getting Help

1. **Check existing connectors:** Look at `source-mysql` or `source-postgres` for patterns
2. **Enable debug logging:** See generated SQL and state
3. **Test incrementally:** Verify each operation before moving to next
4. **Reset state:** When in doubt, clear state and restart
