# Source Connector Coding Standards

**Summary:** Best practices for implementing Airbyte JVM source connectors. Covers code organization, type handling, JDBC patterns, state management, error handling, and common pitfalls. Follow these standards for maintainable, production-ready connectors.

---

## Code Organization

### Package Structure

**Java (Legacy CDK - Postgres style):**
```
source-{db}/src/main/java/io/airbyte/integrations/source/{db}/
├── {DB}Source.java                     # Entry point (main())
├── {DB}SourceOperations.java           # Type conversion
├── {DB}Type.java                       # Database type enum
├── {DB}CatalogHelper.java              # Discovery helpers
├── {DB}QueryUtils.java                 # Query building
├── cdc/
│   ├── {DB}CdcStateHandler.java        # CDC state management
│   ├── {DB}CdcTargetPosition.java      # Position tracking
│   ├── {DB}CdcProperties.java          # Debezium properties
│   ├── {DB}Converter.java              # Debezium record conversion
│   └── {DB}DebeziumStateUtil.java      # State utilities
├── ctid/                               # CTID-based sync (Postgres-specific)
│   ├── {DB}CtidHandler.java
│   └── CtidStateManager.java
├── xmin/                               # XMIN-based sync (Postgres-specific)
│   └── {DB}XminHandler.java
└── cursor_based/
    └── {DB}CursorBasedStateManager.java
```

**Kotlin (Bulk CDK - MySQL style):**
```
source-{db}/src/main/kotlin/io/airbyte/integrations/source/{db}/
├── {DB}Source.kt                       # Entry point (main())
├── {DB}SourceConfigurationSpecification.kt  # Config schema
├── {DB}SourceConfiguration.kt          # Runtime config + factory
├── {DB}SourceMetadataQuerier.kt        # Schema discovery
├── {DB}SourceOperations.kt             # Type mapping + query generation
├── {DB}SourceJdbcPartitionFactory.kt   # Partition creation
├── {DB}SourceJdbcPartition.kt          # Partition types
├── {DB}SourceJdbcStreamStateValue.kt   # Stream state
├── {DB}SourceCdcPosition.kt            # CDC position (if CDC)
├── {DB}SourceDebeziumOperations.kt     # Debezium integration (if CDC)
├── {DB}SourceCdcMetaFields.kt          # CDC meta-fields (if CDC)
└── {DB}SourceCdcBooleanConverter.kt    # Debezium converters (if CDC)
```

### File Naming

**Pattern:** `{DatabaseName}{ComponentType}.{java,kt}`

**Examples:**
- `PostgresSourceOperations.java`
- `MySqlSourceConfiguration.kt`
- `OracleCdcStateHandler.java`

**Avoid:** Generic names like `Operations.kt`, `Config.java`

---

## Naming Conventions

### Java Style

```java
// Classes: PascalCase with prefix
public class PostgresSourceOperations
public class MySqlCdcStateHandler

// Methods: camelCase, verb-based
public JsonNode rowToJson(ResultSet rs)
public void setJsonField(ObjectNode record, ResultSet rs, String name)
public List<TableName> discoverTables()

// Variables: camelCase, descriptive
private final DataSource dataSource;
private final ObjectMapper objectMapper;

// Constants: SCREAMING_SNAKE_CASE
public static final String COLUMN_NAME_AB_CDC_LSN = "_ab_cdc_lsn";
private static final int DEFAULT_FETCH_SIZE = 1000;
```

### Kotlin Style

```kotlin
// Classes: PascalCase with prefix
class MySqlSourceOperations
data class MySqlSourceConfiguration

// Functions: camelCase, verb-based
fun toAirbyteFieldType(column: Column): FieldType
fun generateSelectQuery(stream: Stream): String

// Properties: camelCase
private val config: MySqlSourceConfiguration
private val dataSource: DataSource

// Constants: SCREAMING_SNAKE_CASE in companion object
companion object {
    const val DEFAULT_PORT = 3306
    const val CDC_CURSOR_FIELD = "_ab_cdc_cursor"
}
```

---

## Type Handling

### Type Enum Pattern

```java
public enum PostgresType implements StandardJdbcType {
    BOOLEAN(Types.BOOLEAN),
    INT2(Types.SMALLINT),
    INT4(Types.INTEGER),
    INT8(Types.BIGINT),
    FLOAT4(Types.FLOAT),
    FLOAT8(Types.DOUBLE),
    NUMERIC(Types.NUMERIC),
    VARCHAR(Types.VARCHAR),
    TEXT(Types.LONGVARCHAR),
    DATE(Types.DATE),
    TIME(Types.TIME),
    TIMETZ(Types.TIME_WITH_TIMEZONE),
    TIMESTAMP(Types.TIMESTAMP),
    TIMESTAMPTZ(Types.TIMESTAMP_WITH_TIMEZONE),
    JSON(Types.OTHER),
    JSONB(Types.OTHER),
    BYTEA(Types.BINARY),
    UUID(Types.OTHER),
    UNKNOWN(Types.OTHER);

    private final int jdbcType;

    PostgresType(int jdbcType) {
        this.jdbcType = jdbcType;
    }

    public static PostgresType from(int jdbcType, String typeName) {
        // Handle special types by name first
        return switch (typeName.toLowerCase()) {
            case "json" -> JSON;
            case "jsonb" -> JSONB;
            case "uuid" -> UUID;
            case "bytea" -> BYTEA;
            default -> fromJdbcType(jdbcType);
        };
    }
}
```

### Type Conversion Pattern

```java
@Override
public void setJsonField(ObjectNode record, ResultSet rs, String columnName)
    throws SQLException {
    PostgresType type = getColumnType(rs.getMetaData(), columnName);

    // Handle NULL first
    if (rs.getObject(columnName) == null) {
        record.putNull(columnName);
        return;
    }

    switch (type) {
        case BOOLEAN -> record.put(columnName, rs.getBoolean(columnName));
        case INT2, INT4 -> record.put(columnName, rs.getInt(columnName));
        case INT8 -> record.put(columnName, rs.getLong(columnName));
        case FLOAT4, FLOAT8 -> record.put(columnName, rs.getDouble(columnName));
        case NUMERIC -> record.put(columnName, rs.getBigDecimal(columnName));
        case VARCHAR, TEXT -> record.put(columnName, rs.getString(columnName));
        case DATE -> handleDate(record, rs, columnName);
        case TIMESTAMP -> handleTimestamp(record, rs, columnName);
        case TIMESTAMPTZ -> handleTimestampTz(record, rs, columnName);
        case JSON, JSONB -> handleJson(record, rs, columnName);
        case BYTEA -> handleBinary(record, rs, columnName);
        case UUID -> handleUuid(record, rs, columnName);
        default -> record.put(columnName, rs.getString(columnName));
    }
}
```

### Date/Time Formatting

```java
// Use ISO 8601 formats consistently
private static final DateTimeFormatter DATE_FORMATTER =
    DateTimeFormatter.ISO_LOCAL_DATE;

private static final DateTimeFormatter TIMESTAMP_FORMATTER =
    DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS");

private static final DateTimeFormatter TIMESTAMP_TZ_FORMATTER =
    DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX");

private void handleDate(ObjectNode record, ResultSet rs, String name)
    throws SQLException {
    Date date = rs.getDate(name);
    record.put(name, date.toLocalDate().format(DATE_FORMATTER));
}

private void handleTimestamp(ObjectNode record, ResultSet rs, String name)
    throws SQLException {
    Timestamp ts = rs.getTimestamp(name);
    record.put(name, ts.toLocalDateTime().format(TIMESTAMP_FORMATTER));
}

private void handleTimestampTz(ObjectNode record, ResultSet rs, String name)
    throws SQLException {
    OffsetDateTime odt = rs.getObject(name, OffsetDateTime.class);
    record.put(name, odt.format(TIMESTAMP_TZ_FORMATTER));
}
```

---

## JDBC Patterns

### Resource Management

```java
// Always use try-with-resources
public List<TableName> listTables() {
    try (Connection conn = dataSource.getConnection();
         ResultSet rs = conn.getMetaData().getTables(null, null, "%", TABLE_TYPES)) {

        List<TableName> tables = new ArrayList<>();
        while (rs.next()) {
            tables.add(new TableName(
                rs.getString("TABLE_SCHEM"),
                rs.getString("TABLE_NAME")
            ));
        }
        return tables;

    } catch (SQLException e) {
        throw new RuntimeException("Failed to list tables", e);
    }
}

// Streaming large result sets
public void streamTable(String query, Consumer<ResultSet> processor) {
    try (Connection conn = dataSource.getConnection()) {
        conn.setAutoCommit(false);  // Required for streaming

        try (Statement stmt = conn.createStatement()) {
            stmt.setFetchSize(FETCH_SIZE);  // Enable streaming

            try (ResultSet rs = stmt.executeQuery(query)) {
                while (rs.next()) {
                    processor.accept(rs);
                }
            }
        }
    } catch (SQLException e) {
        throw new RuntimeException("Failed to stream table", e);
    }
}
```

### Prepared Statements

```java
// Use PreparedStatement for parameterized queries
public long countTableWithCursor(TableName table, String cursorField, String cursorValue) {
    String sql = String.format(
        "SELECT COUNT(*) FROM %s WHERE %s > ?",
        table.fullName(),
        quoteIdentifier(cursorField)
    );

    try (Connection conn = dataSource.getConnection();
         PreparedStatement stmt = conn.prepareStatement(sql)) {

        stmt.setString(1, cursorValue);

        try (ResultSet rs = stmt.executeQuery()) {
            return rs.next() ? rs.getLong(1) : 0L;
        }

    } catch (SQLException e) {
        throw new RuntimeException("Failed to count table", e);
    }
}
```

### Identifier Quoting

```java
// Postgres: double quotes
public String quoteIdentifier(String identifier) {
    return "\"" + identifier.replace("\"", "\"\"") + "\"";
}

// MySQL: backticks
public String quoteIdentifier(String identifier) {
    return "`" + identifier.replace("`", "``") + "`";
}

// SQL Server: square brackets
public String quoteIdentifier(String identifier) {
    return "[" + identifier.replace("]", "]]") + "]";
}

// Use for all identifiers in queries
String query = String.format(
    "SELECT %s FROM %s.%s",
    columns.stream().map(this::quoteIdentifier).collect(joining(", ")),
    quoteIdentifier(schema),
    quoteIdentifier(table)
);
```

---

## State Management

### Cursor State Pattern

```java
public class CursorBasedStateManager {
    private final ConfiguredAirbyteStream stream;
    private String lastCursorValue;

    public void updateState(JsonNode record) {
        String cursorField = stream.getCursorField().get(0);
        JsonNode cursorNode = record.get(cursorField);
        if (cursorNode != null && !cursorNode.isNull()) {
            lastCursorValue = cursorNode.asText();
        }
    }

    public AirbyteStateMessage createStateMessage() {
        return new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor()
                    .withName(stream.getStream().getName())
                    .withNamespace(stream.getStream().getNamespace()))
                .withStreamState(Jsons.jsonNode(Map.of(
                    "cursor_field", stream.getCursorField(),
                    "cursor", lastCursorValue
                ))));
    }
}
```

### State Emission Timing

```java
// Emit state periodically during reads
public Iterator<AirbyteMessage> readIncremental(
    ConfiguredAirbyteStream stream,
    JsonNode state
) {
    return new Iterator<>() {
        private final ResultSet rs = executeQuery(buildQuery(stream, state));
        private int recordCount = 0;
        private final CursorBasedStateManager stateManager = new CursorBasedStateManager(stream);

        @Override
        public boolean hasNext() {
            try {
                return rs.next();
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        }

        @Override
        public AirbyteMessage next() {
            try {
                JsonNode data = rowToJson(rs);
                stateManager.updateState(data);
                recordCount++;

                // Emit state every 10000 records
                if (recordCount % 10000 == 0) {
                    // Return state message (caller should handle interleaving)
                }

                return createRecordMessage(stream, data);

            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        }
    };
}
```

### CDC State Pattern

```java
public class CdcStateManager {
    private CdcPosition currentPosition;
    private final Map<StreamDescriptor, JsonNode> streamStates = new HashMap<>();

    public void updatePosition(CdcPosition position) {
        this.currentPosition = position;
    }

    public void updateStreamState(StreamDescriptor stream, JsonNode state) {
        streamStates.put(stream, state);
    }

    public AirbyteStateMessage createGlobalState() {
        return new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(new AirbyteGlobalState()
                .withSharedState(currentPosition.toJson())
                .withStreamStates(streamStates.entrySet().stream()
                    .map(e -> new AirbyteStreamState()
                        .withStreamDescriptor(e.getKey())
                        .withStreamState(e.getValue()))
                    .toList()));
    }
}
```

---

## Error Handling

### Exception Classification

```java
public AirbyteConnectionStatus check(JsonNode config) {
    try {
        // Attempt connection
        try (Connection conn = createConnection(config)) {
            conn.createStatement().execute("SELECT 1");
        }
        return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);

    } catch (SQLException e) {
        return new AirbyteConnectionStatus()
            .withStatus(Status.FAILED)
            .withMessage(classifyError(e));
    }
}

private String classifyError(SQLException e) {
    String sqlState = e.getSQLState();
    String message = e.getMessage().toLowerCase();

    // Authentication errors
    if (sqlState != null && sqlState.startsWith("28")) {
        return "Authentication failed. Check username and password.";
    }

    // Connection errors
    if (sqlState != null && sqlState.startsWith("08")) {
        return "Connection failed. Check host, port, and network connectivity.";
    }

    // Permission errors
    if (message.contains("permission denied") ||
        message.contains("access denied")) {
        return "Permission denied. Grant appropriate privileges to user.";
    }

    // Database not found
    if (message.contains("does not exist") ||
        message.contains("unknown database")) {
        return "Database not found. Check database name.";
    }

    // Default
    return "Connection failed: " + e.getMessage();
}
```

### Actionable Error Messages

```java
// Good: Specific and actionable
throw new ConfigErrorException(
    "Permission denied: Cannot SELECT from table 'users'.\n\n" +
    "Required permission:\n" +
    "  GRANT SELECT ON users TO " + config.getUsername() + ";\n\n" +
    "Or grant on all tables:\n" +
    "  GRANT SELECT ON ALL TABLES IN SCHEMA public TO " + config.getUsername() + ";"
);

// Bad: Vague
throw new ConfigErrorException("Access denied");
throw new ConfigErrorException(e.getMessage());  // Raw database message
```

---

## Logging Patterns

### Log Levels

```java
private static final Logger LOGGER = LoggerFactory.getLogger(MySource.class);

// INFO: Normal operations
LOGGER.info("Starting discovery for database: {}", config.getDatabase());
LOGGER.info("Found {} tables", tables.size());
LOGGER.info("Beginning read for stream: {}", stream.getName());
LOGGER.info("Emitting state after {} records", recordCount);

// WARN: Unexpected but recoverable
LOGGER.warn("Column {} has unknown type {}, treating as STRING", columnName, typeName);
LOGGER.warn("Cursor column {} is nullable, may cause duplicates", cursorField);

// ERROR: Failures
LOGGER.error("Failed to read from table {}: {}", tableName, e.getMessage(), e);
LOGGER.error("CDC position {} is no longer available", savedPosition);

// DEBUG: Detailed diagnostics
LOGGER.debug("Executing query: {}", query);
LOGGER.debug("Received {} bytes from ResultSet", bytes.length);
LOGGER.debug("Type mapping: {} -> {}", dbType, airbyteType);
```

### Structured Logging

```java
// Include context in log messages
LOGGER.info("Reading stream: name={}, namespace={}, syncMode={}",
    stream.getName(), stream.getNamespace(), stream.getSyncMode());

LOGGER.info("Checkpoint: stream={}, cursor={}, records={}",
    stream.getName(), cursorValue, recordCount);

LOGGER.error("Query failed: table={}, error={}, sqlState={}",
    tableName, e.getMessage(), e.getSQLState());
```

---

## Common Gotchas

### 1. Memory Management

```java
// Bad: Loading entire table into memory
List<JsonNode> records = new ArrayList<>();
while (rs.next()) {
    records.add(rowToJson(rs));  // OOM for large tables!
}

// Good: Stream records with fetch size
try (Connection conn = dataSource.getConnection()) {
    conn.setAutoCommit(false);

    try (Statement stmt = conn.createStatement()) {
        stmt.setFetchSize(1000);  // Stream results

        try (ResultSet rs = stmt.executeQuery(query)) {
            while (rs.next()) {
                yield rowToJson(rs);  // Process one at a time
            }
        }
    }
}
```

### 2. Null Handling

```java
// Bad: Not checking for null
String value = rs.getString(columnName);
record.put(columnName, value);  // NPE or incorrect null handling

// Good: Explicit null check
Object value = rs.getObject(columnName);
if (value == null || rs.wasNull()) {
    record.putNull(columnName);
} else {
    record.put(columnName, convertValue(value));
}
```

### 3. Timestamp Timezone Handling

```java
// Bad: Losing timezone information
Timestamp ts = rs.getTimestamp(columnName);
record.put(columnName, ts.toString());  // Wrong format, loses TZ

// Good: Preserve timezone
OffsetDateTime odt = rs.getObject(columnName, OffsetDateTime.class);
record.put(columnName, odt.format(DateTimeFormatter.ISO_OFFSET_DATE_TIME));

// Or for databases without timezone support
Timestamp ts = rs.getTimestamp(columnName, Calendar.getInstance(TimeZone.getTimeZone("UTC")));
record.put(columnName, ts.toInstant().toString());
```

### 4. SQL Injection in Discovery

```java
// Bad: String concatenation
String query = "SELECT * FROM " + tableName + " WHERE " + cursorField + " > " + cursorValue;

// Good: Use prepared statements
String query = "SELECT * FROM " + quoteIdentifier(tableName) +
    " WHERE " + quoteIdentifier(cursorField) + " > ?";
PreparedStatement stmt = conn.prepareStatement(query);
stmt.setString(1, cursorValue);
```

### 5. Connection Leaks

```java
// Bad: Connection not closed on exception
Connection conn = dataSource.getConnection();
ResultSet rs = conn.createStatement().executeQuery(query);
// Exception here = connection leak!

// Good: Try-with-resources
try (Connection conn = dataSource.getConnection();
     Statement stmt = conn.createStatement();
     ResultSet rs = stmt.executeQuery(query)) {
    // Process results
}
```

### 6. State Not Updated Before Emission

```java
// Bad: State emitted with stale cursor
while (rs.next()) {
    yield createRecord(rs);
    recordCount++;
    if (recordCount % 10000 == 0) {
        yield createState(cursorValue);  // cursorValue not updated!
    }
    cursorValue = rs.getString(cursorField);  // Update after emit!
}

// Good: Update state before emission
while (rs.next()) {
    cursorValue = rs.getString(cursorField);  // Update first
    yield createRecord(rs);
    recordCount++;
    if (recordCount % 10000 == 0) {
        yield createState(cursorValue);  // Correct value
    }
}
```

### 7. Missing Final State Emission

```java
// Bad: No final state
while (rs.next()) {
    yield createRecord(rs);
    if (recordCount % 10000 == 0) {
        yield createState(cursorValue);
    }
}
// Stream ends without final state!

// Good: Always emit final state
while (rs.next()) {
    yield createRecord(rs);
    if (recordCount % 10000 == 0) {
        yield createState(cursorValue);
    }
}
yield createState(cursorValue);  // Final state
```

### 8. Cursor Column Not Indexed

```java
// Check if cursor column is indexed
private void validateCursorColumn(TableName table, String cursorField) {
    Set<String> indexedColumns = getIndexedColumns(table);
    if (!indexedColumns.contains(cursorField)) {
        LOGGER.warn(
            "Cursor column {} is not indexed. " +
            "Incremental syncs may be slow for large tables. " +
            "Consider adding an index: CREATE INDEX ON {} ({})",
            cursorField, table.fullName(), cursorField
        );
    }
}
```

---

## Testing Patterns

### Unit Tests

```java
class MySourceOperationsTest {

    private MySourceOperations operations;

    @BeforeEach
    void setUp() {
        operations = new MySourceOperations();
    }

    @Test
    void testTypeMapping() {
        assertEquals(JsonSchemaType.INTEGER, operations.getAirbyteType(MyType.BIGINT));
        assertEquals(JsonSchemaType.STRING, operations.getAirbyteType(MyType.VARCHAR));
        assertEquals(JsonSchemaType.OBJECT, operations.getAirbyteType(MyType.JSON));
    }

    @Test
    void testTimestampFormatting() {
        Timestamp ts = Timestamp.valueOf("2024-01-15 10:30:45.123456");
        String formatted = operations.formatTimestamp(ts);
        assertEquals("2024-01-15T10:30:45.123456", formatted);
    }
}
```

### Integration Tests with Testcontainers

```java
@Testcontainers
class MySourceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
        .withDatabaseName("test")
        .withUsername("test")
        .withPassword("test");

    private MySource source;

    @BeforeEach
    void setUp() {
        source = new MySource();
        // Insert test data
        try (Connection conn = DriverManager.getConnection(
            postgres.getJdbcUrl(),
            postgres.getUsername(),
            postgres.getPassword()
        )) {
            conn.createStatement().execute("""
                CREATE TABLE test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    updated_at TIMESTAMP
                )
            """);
            conn.createStatement().execute("""
                INSERT INTO test_table (name, updated_at) VALUES
                    ('Alice', '2024-01-01 10:00:00'),
                    ('Bob', '2024-01-02 10:00:00')
            """);
        }
    }

    @Test
    void testDiscover() {
        JsonNode config = createConfig();
        AirbyteCatalog catalog = source.discover(config);

        assertNotNull(catalog);
        assertEquals(1, catalog.getStreams().size());
        assertEquals("test_table", catalog.getStreams().get(0).getName());
    }

    @Test
    void testRead() {
        JsonNode config = createConfig();
        ConfiguredAirbyteCatalog catalog = createCatalog();

        List<AirbyteMessage> messages = new ArrayList<>();
        source.read(config, catalog, null).forEachRemaining(messages::add);

        long recordCount = messages.stream()
            .filter(m -> m.getType() == Type.RECORD)
            .count();
        assertEquals(2, recordCount);
    }
}
```

---

## Style Summary

**Naming:**
- Classes: PascalCase with database prefix (`PostgresSourceOperations`)
- Methods: camelCase, verbs (`rowToJson`, `getAirbyteType`)
- Variables: camelCase, descriptive (`cursorValue`, `lastEmittedAt`)
- Constants: SCREAMING_SNAKE_CASE (`DEFAULT_FETCH_SIZE`)

**Types:**
- Use enum for database types
- Explicit null handling in all conversions
- ISO 8601 for all date/time formatting

**JDBC:**
- Always use try-with-resources
- Set fetchSize for streaming
- Use PreparedStatement for parameters
- Quote all identifiers

**State:**
- Update before emitting
- Emit periodically (every N records)
- Always emit final state

**Errors:**
- Classify by recoverability (Config/Transient/System)
- Provide actionable messages
- Include context (table name, column, SQL state)

**Logging:**
- INFO for operations and checkpoints
- WARN for unexpected but recoverable
- ERROR with full context
- DEBUG for queries and detailed diagnostics

---

## Quick Reference: Most Common Mistakes

1. Not setting `fetchSize` -> OOM on large tables
2. Not checking for NULL -> incorrect data or NPE
3. Losing timezone information -> incorrect timestamps
4. SQL injection in dynamic queries -> security vulnerability
5. Connection leaks -> pool exhaustion
6. Emitting stale state -> duplicate data on resume
7. No final state emission -> lost progress
8. Unindexed cursor column -> slow incremental syncs
9. Raw database errors -> confusing error messages
10. Not streaming results -> memory issues
