# Source Connector Implementation Reference

**Summary:** Quick reference for implementing JVM source connectors. Covers the core components, type mapping, sync modes, CDC integration, and state management. Use as a lookup guide during development.

---

## The Core Components

### 1. Source Operations

**Purpose:** Convert database types to Airbyte types

**Key Methods:**

```kotlin
interface SourceOperations<ResultSetType, DatabaseType> {
    // Map database type to JSON Schema type
    fun getAirbyteType(databaseType: DatabaseType): JsonSchemaType

    // Extract value from ResultSet and add to JSON record
    fun setJsonField(record: ObjectNode, rs: ResultSetType, columnName: String)

    // Convert ResultSet row to Airbyte record data
    fun rowToJson(rs: ResultSetType): JsonNode
}
```

**Implementation Pattern (Java):**
```java
public class MySourceOperations
    extends AbstractJdbcCompatibleSourceOperations<MyDatabaseType> {

    @Override
    public void setJsonField(ObjectNode record, ResultSet rs, String columnName)
        throws SQLException {
        MyDatabaseType type = getColumnType(rs.getMetaData(), columnName);

        if (rs.getObject(columnName) == null) {
            record.putNull(columnName);
            return;
        }

        switch (type) {
            case BOOLEAN -> record.put(columnName, rs.getBoolean(columnName));
            case SMALLINT, INTEGER -> record.put(columnName, rs.getInt(columnName));
            case BIGINT -> record.put(columnName, rs.getLong(columnName));
            case FLOAT, DOUBLE -> record.put(columnName, rs.getDouble(columnName));
            case DECIMAL -> record.put(columnName, rs.getBigDecimal(columnName));
            case VARCHAR, TEXT -> record.put(columnName, rs.getString(columnName));
            case DATE -> record.put(columnName, formatDate(rs.getDate(columnName)));
            case TIMESTAMP -> record.put(columnName, formatTimestamp(rs.getTimestamp(columnName)));
            case TIMESTAMP_WITH_TIMEZONE -> record.put(columnName,
                formatTimestampTz(rs.getObject(columnName, OffsetDateTime.class)));
            case JSON, JSONB -> record.set(columnName, parseJson(rs.getString(columnName)));
            case BYTEA -> record.put(columnName, Base64.encode(rs.getBytes(columnName)));
            default -> record.put(columnName, rs.getString(columnName));
        }
    }

    @Override
    public JsonSchemaType getAirbyteType(MyDatabaseType type) {
        return switch (type) {
            case BOOLEAN -> JsonSchemaType.BOOLEAN;
            case SMALLINT, INTEGER, BIGINT -> JsonSchemaType.INTEGER;
            case FLOAT, DOUBLE, DECIMAL -> JsonSchemaType.NUMBER;
            case DATE -> JsonSchemaType.STRING_DATE;
            case TIMESTAMP -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
            case TIMESTAMP_WITH_TIMEZONE -> JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE;
            case JSON, JSONB -> JsonSchemaType.OBJECT;
            case BYTEA -> JsonSchemaType.STRING_BASE64;
            default -> JsonSchemaType.STRING;
        };
    }
}
```

**Implementation Pattern (Kotlin - Bulk CDK):**
```kotlin
class MySqlSourceOperations : FieldTypeMapper, SelectQueryGenerator {

    override fun toAirbyteFieldType(column: Column): FieldType {
        return when (column.type.lowercase()) {
            "tinyint", "smallint", "mediumint", "int", "bigint" -> IntegerType
            "float", "double", "decimal" -> NumberType
            "char", "varchar", "text", "longtext" -> StringType
            "date" -> DateType
            "datetime", "timestamp" -> TimestampType
            "json" -> ObjectType(emptyMap())
            "tinyint(1)", "bit" -> BooleanType
            else -> StringType
        }
    }

    override fun generateSelectQuery(
        stream: Stream,
        columns: List<String>,
        cursor: CursorValue?,
    ): String {
        val columnList = columns.joinToString(", ") { "`$it`" }
        val table = "`${stream.namespace}`.`${stream.name}`"

        return if (cursor != null) {
            """
            SELECT $columnList FROM $table
            WHERE `${cursor.field}` > ?
            ORDER BY `${cursor.field}` ASC
            """.trimIndent()
        } else {
            "SELECT $columnList FROM $table"
        }
    }
}
```

---

### 2. Database Type Enum

**Purpose:** Map database-specific types to enumeration

**Pattern:**
```java
public enum MyDatabaseType implements StandardJdbcType {
    // Numeric types
    BOOLEAN(Types.BOOLEAN),
    SMALLINT(Types.SMALLINT),
    INTEGER(Types.INTEGER),
    BIGINT(Types.BIGINT),
    FLOAT(Types.FLOAT),
    DOUBLE(Types.DOUBLE),
    DECIMAL(Types.DECIMAL),

    // String types
    CHAR(Types.CHAR),
    VARCHAR(Types.VARCHAR),
    TEXT(Types.LONGVARCHAR),

    // Date/Time types
    DATE(Types.DATE),
    TIME(Types.TIME),
    TIMESTAMP(Types.TIMESTAMP),
    TIMESTAMP_WITH_TIMEZONE(Types.TIMESTAMP_WITH_TIMEZONE),

    // Special types
    JSON(Types.OTHER),
    JSONB(Types.OTHER),
    BYTEA(Types.BINARY),
    UUID(Types.OTHER),

    // Unknown
    UNKNOWN(Types.OTHER);

    private final int jdbcType;

    MyDatabaseType(int jdbcType) {
        this.jdbcType = jdbcType;
    }

    public static MyDatabaseType fromJdbcType(int jdbcType, String typeName) {
        return switch (typeName.toLowerCase()) {
            case "json" -> JSON;
            case "jsonb" -> JSONB;
            case "uuid" -> UUID;
            case "bytea" -> BYTEA;
            default -> fromJdbcTypeCode(jdbcType);
        };
    }

    private static MyDatabaseType fromJdbcTypeCode(int code) {
        for (MyDatabaseType type : values()) {
            if (type.jdbcType == code) return type;
        }
        return UNKNOWN;
    }
}
```

---

### 3. Metadata Querier

**Purpose:** Discover schema from database catalog

**Key Methods:**

```kotlin
interface MetadataQuerier {
    fun listTables(): List<TableName>
    fun getColumns(table: TableName): List<Column>
    fun getPrimaryKeys(table: TableName): List<String>
}
```

**Implementation:**
```kotlin
class MyMetadataQuerier(
    private val dataSource: DataSource,
) : MetadataQuerier {

    override fun listTables(): List<TableName> {
        dataSource.connection.use { conn ->
            val rs = conn.metaData.getTables(
                null,           // catalog
                null,           // schema pattern
                "%",            // table name pattern
                arrayOf("TABLE")  // table types
            )
            val tables = mutableListOf<TableName>()
            while (rs.next()) {
                tables.add(TableName(
                    catalog = rs.getString("TABLE_CAT"),
                    schema = rs.getString("TABLE_SCHEM"),
                    name = rs.getString("TABLE_NAME")
                ))
            }
            return tables
        }
    }

    override fun getColumns(table: TableName): List<Column> {
        dataSource.connection.use { conn ->
            val rs = conn.metaData.getColumns(
                table.catalog,
                table.schema,
                table.name,
                "%"
            )
            val columns = mutableListOf<Column>()
            while (rs.next()) {
                columns.add(Column(
                    name = rs.getString("COLUMN_NAME"),
                    type = rs.getString("TYPE_NAME"),
                    jdbcType = rs.getInt("DATA_TYPE"),
                    nullable = rs.getInt("NULLABLE") == DatabaseMetaData.columnNullable,
                    position = rs.getInt("ORDINAL_POSITION")
                ))
            }
            return columns.sortedBy { it.position }
        }
    }

    override fun getPrimaryKeys(table: TableName): List<String> {
        dataSource.connection.use { conn ->
            val rs = conn.metaData.getPrimaryKeys(
                table.catalog,
                table.schema,
                table.name
            )
            val pks = mutableListOf<Pair<String, Int>>()
            while (rs.next()) {
                pks.add(Pair(
                    rs.getString("COLUMN_NAME"),
                    rs.getInt("KEY_SEQ")
                ))
            }
            return pks.sortedBy { it.second }.map { it.first }
        }
    }
}
```

**Alternative: Direct SQL Queries:**
```kotlin
override fun listTables(): List<TableName> {
    val sql = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('information_schema', 'pg_catalog', 'mysql')
    """.trimIndent()

    return executeQuery(sql) { rs ->
        TableName(schema = rs.getString(1), name = rs.getString(2))
    }
}

override fun getColumns(table: TableName): List<Column> {
    val sql = """
        SELECT column_name, data_type, is_nullable, ordinal_position
        FROM information_schema.columns
        WHERE table_schema = ? AND table_name = ?
        ORDER BY ordinal_position
    """.trimIndent()

    return executeQuery(sql, table.schema, table.name) { rs ->
        Column(
            name = rs.getString("column_name"),
            type = rs.getString("data_type"),
            nullable = rs.getString("is_nullable") == "YES",
            position = rs.getInt("ordinal_position")
        )
    }
}
```

---

### 4. Configuration

**Specification (JSON Schema generation):**
```kotlin
@JsonSchemaTitle("My Database Source Spec")
class MySourceSpecification : ConfigurationSpecification {

    @get:JsonProperty("host")
    @get:JsonSchemaTitle("Host")
    @get:JsonSchemaDescription("Database server hostname")
    lateinit var host: String

    @get:JsonProperty("port")
    @get:JsonSchemaTitle("Port")
    @get:JsonSchemaDefault("5432")
    var port: Int = 5432

    @get:JsonProperty("database")
    @get:JsonSchemaTitle("Database Name")
    lateinit var database: String

    @get:JsonProperty("username")
    @get:JsonSchemaTitle("Username")
    lateinit var username: String

    @get:JsonProperty("password")
    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyOrder(5)
    @get:JsonSchemaFormat("password")
    var password: String? = null

    @get:JsonProperty("ssl_mode")
    @get:JsonSchemaTitle("SSL Mode")
    @get:JsonSchemaDefault("prefer")
    var sslMode: SslMode = SslMode.PREFER

    @get:JsonProperty("replication_method")
    @get:JsonSchemaTitle("Update Method")
    var replicationMethod: ReplicationMethod = ReplicationMethod()
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
@JsonSubTypes(
    JsonSubTypes.Type(value = Standard::class, name = "STANDARD"),
    JsonSubTypes.Type(value = Cdc::class, name = "CDC")
)
sealed class ReplicationMethod {
    class Standard : ReplicationMethod()
    class Cdc(
        @get:JsonProperty("initial_waiting_seconds")
        val initialWaitingSeconds: Int = 300
    ) : ReplicationMethod()
}
```

**Runtime Configuration:**
```kotlin
data class MySourceConfiguration(
    val host: String,
    val port: Int,
    val database: String,
    val username: String,
    val password: String?,
    val sslMode: SslMode,
    val replicationMethod: ReplicationMethod,
) : JdbcSourceConfiguration {

    override fun toJdbcUrl(): String {
        return "jdbc:mydb://$host:$port/$database"
    }

    override fun toJdbcProperties(): Properties {
        return Properties().apply {
            setProperty("user", username)
            password?.let { setProperty("password", it) }
            setProperty("ssl", sslMode != SslMode.DISABLE)
        }
    }

    fun isCdcEnabled(): Boolean = replicationMethod is Cdc
}
```

**Configuration Factory:**
```kotlin
class MySourceConfigurationFactory : ConfigurationFactory<MySourceConfiguration> {

    override fun make(spec: ConfigurationSpecification): MySourceConfiguration {
        val mySpec = spec as MySourceSpecification
        return MySourceConfiguration(
            host = mySpec.host,
            port = mySpec.port,
            database = mySpec.database,
            username = mySpec.username,
            password = mySpec.password,
            sslMode = mySpec.sslMode,
            replicationMethod = mySpec.replicationMethod,
        )
    }
}
```

---

### 5. State Management

**Cursor-Based State:**
```kotlin
data class CursorBasedState(
    @JsonProperty("cursor_field")
    val cursorField: List<String>,

    @JsonProperty("cursor")
    val cursor: String?,

    @JsonProperty("state_type")
    val stateType: StateType = StateType.CURSOR_BASED,
)

enum class StateType {
    PRIMARY_KEY,    // Initial snapshot using PK checkpoint
    CURSOR_BASED,   // Incremental using cursor
}
```

**CDC State:**
```kotlin
// Postgres
data class PostgresCdcState(
    @JsonProperty("lsn")
    val lsn: Long,

    @JsonProperty("txId")
    val transactionId: Long?,
)

// MySQL
data class MySqlCdcState(
    @JsonProperty("file")
    val binlogFile: String,

    @JsonProperty("pos")
    val binlogPosition: Long,

    @JsonProperty("gtid")
    val gtidSet: String?,
)
```

**State Message Emission:**
```kotlin
fun emitStreamState(
    stream: StreamDescriptor,
    cursorField: String,
    cursorValue: String?,
): AirbyteMessage {
    return AirbyteMessage()
        .withType(Type.STATE)
        .withState(
            AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(stream)
                        .withStreamState(
                            Jsons.jsonNode(CursorBasedState(
                                cursorField = listOf(cursorField),
                                cursor = cursorValue,
                            ))
                        )
                )
        )
}

fun emitGlobalState(
    cdcState: CdcState,
    streamStates: List<AirbyteStreamState>,
): AirbyteMessage {
    return AirbyteMessage()
        .withType(Type.STATE)
        .withState(
            AirbyteStateMessage()
                .withType(AirbyteStateType.GLOBAL)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(Jsons.jsonNode(cdcState))
                        .withStreamStates(streamStates)
                )
        )
}
```

---

### 6. Exception Handler

**Purpose:** Classify database errors

```kotlin
class MySourceExceptionHandler : ConnectorExceptionHandler {

    override fun handle(e: Throwable): AirbyteTraceMessage {
        val (type, message) = classifyException(e)
        return AirbyteTraceMessage()
            .withType(AirbyteTraceMessage.Type.ERROR)
            .withError(
                AirbyteErrorTraceMessage()
                    .withFailureType(type)
                    .withMessage(message)
                    .withStackTrace(ExceptionUtils.getStackTrace(e))
            )
    }

    private fun classifyException(e: Throwable): Pair<FailureType, String> {
        val message = e.message?.lowercase() ?: ""

        return when {
            // Config errors (user must fix)
            message.contains("access denied") ||
            message.contains("authentication failed") ->
                FailureType.CONFIG_ERROR to
                "Authentication failed. Check username and password."

            message.contains("unknown database") ||
            message.contains("does not exist") ->
                FailureType.CONFIG_ERROR to
                "Database not found. Check database name."

            message.contains("permission denied") ->
                FailureType.CONFIG_ERROR to
                "Permission denied. Grant SELECT privilege to user."

            // Transient errors (will retry)
            message.contains("connection refused") ||
            message.contains("connection reset") ||
            message.contains("timeout") ->
                FailureType.TRANSIENT_ERROR to
                "Connection error. Will retry automatically."

            e is SQLException && e.sqlState?.startsWith("08") == true ->
                FailureType.TRANSIENT_ERROR to
                "Database connection error: ${e.message}"

            // System errors (internal)
            else ->
                FailureType.SYSTEM_ERROR to
                "Unexpected error: ${e.message}"
        }
    }
}
```

---

## Type Mapping Reference

### Common Type Mappings

| Airbyte Type | Postgres | MySQL | SQL Server | Oracle |
|--------------|----------|-------|------------|--------|
| `BOOLEAN` | boolean | tinyint(1), bit | bit | NUMBER(1) |
| `INTEGER` | smallint, int, bigint | tinyint, smallint, int, bigint | tinyint, smallint, int, bigint | NUMBER (no scale) |
| `NUMBER` | decimal, numeric, float, double | decimal, float, double | decimal, float, real | NUMBER, FLOAT |
| `STRING` | varchar, text, char | varchar, text, char | varchar, nvarchar, text | VARCHAR2, CLOB |
| `DATE` | date | date | date | DATE |
| `TIMESTAMP` | timestamp | datetime, timestamp | datetime, datetime2 | TIMESTAMP |
| `TIMESTAMP_TZ` | timestamptz | N/A | datetimeoffset | TIMESTAMP WITH TZ |
| `TIME` | time | time | time | N/A |
| `TIME_TZ` | timetz | N/A | N/A | N/A |
| `OBJECT` | json, jsonb | json | N/A | N/A |
| `ARRAY` | array types | N/A | N/A | N/A |
| `BINARY` | bytea | blob, binary | varbinary, image | BLOB, RAW |

### Timestamp Formatting

```kotlin
// ISO 8601 formats
const val DATE_FORMAT = "yyyy-MM-dd"
const val TIME_FORMAT = "HH:mm:ss.SSSSSS"
const val TIMESTAMP_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
const val TIMESTAMP_TZ_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX"

fun formatDate(date: Date?): String? =
    date?.toLocalDate()?.format(DateTimeFormatter.ISO_LOCAL_DATE)

fun formatTimestamp(ts: Timestamp?): String? =
    ts?.toLocalDateTime()?.format(DateTimeFormatter.ofPattern(TIMESTAMP_FORMAT))

fun formatTimestampTz(odt: OffsetDateTime?): String? =
    odt?.format(DateTimeFormatter.ofPattern(TIMESTAMP_TZ_FORMAT))
```

### Special Type Handling

**JSON/JSONB:**
```kotlin
fun handleJson(rs: ResultSet, columnName: String): JsonNode {
    val jsonStr = rs.getString(columnName)
    return if (jsonStr != null) {
        objectMapper.readTree(jsonStr)
    } else {
        NullNode.instance
    }
}
```

**Arrays:**
```kotlin
fun handleArray(rs: ResultSet, columnName: String): ArrayNode {
    val array = rs.getArray(columnName)
    val arrayNode = objectMapper.createArrayNode()
    if (array != null) {
        val elements = array.array as Array<*>
        elements.forEach { arrayNode.add(convertToJson(it)) }
    }
    return arrayNode
}
```

**Binary:**
```kotlin
fun handleBinary(rs: ResultSet, columnName: String): String? {
    val bytes = rs.getBytes(columnName)
    return bytes?.let { Base64.getEncoder().encodeToString(it) }
}
```

**UUID:**
```kotlin
fun handleUuid(rs: ResultSet, columnName: String): String? {
    return rs.getObject(columnName, UUID::class.java)?.toString()
}
```

---

## Sync Mode Queries

### Full Refresh

**Simple:**
```sql
SELECT * FROM schema.table
```

**With Primary Key Order (resumable):**
```sql
SELECT * FROM schema.table
ORDER BY pk_col1, pk_col2
```

**Postgres CTID-Based (chunked):**
```sql
SELECT ctid, * FROM schema.table
WHERE ctid > '(last_page, last_offset)'::tid
ORDER BY ctid
LIMIT 10000
```

**MySQL PK-Based (chunked):**
```sql
SELECT * FROM schema.table
WHERE id > ?
ORDER BY id
LIMIT 10000
```

### Incremental (Cursor-Based)

**Timestamp Cursor:**
```sql
SELECT * FROM schema.table
WHERE updated_at > ?
ORDER BY updated_at ASC
LIMIT 10000
```

**Integer Cursor:**
```sql
SELECT * FROM schema.table
WHERE id > ?
ORDER BY id ASC
LIMIT 10000
```

**Composite Cursor:**
```sql
SELECT * FROM schema.table
WHERE (cursor_col1, cursor_col2) > (?, ?)
ORDER BY cursor_col1, cursor_col2
LIMIT 10000
```

### CDC Queries

**Postgres Snapshot:**
```sql
-- Set transaction snapshot for consistency
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT pg_current_wal_lsn();  -- Save position

SELECT * FROM schema.table ORDER BY pk;

COMMIT;
-- Then start streaming from saved LSN
```

**MySQL Snapshot:**
```sql
-- Lock tables for consistent snapshot
FLUSH TABLES WITH READ LOCK;
SHOW MASTER STATUS;  -- Save binlog position

SELECT * FROM schema.table ORDER BY pk;

UNLOCK TABLES;
-- Then start streaming from saved position
```

---

## CDC Integration

### Debezium Properties

**Postgres:**
```kotlin
fun postgresDebeziumProperties(config: PostgresConfig): Properties {
    return Properties().apply {
        put("connector.class", "io.debezium.connector.postgresql.PostgresConnector")
        put("database.hostname", config.host)
        put("database.port", config.port.toString())
        put("database.user", config.username)
        put("database.password", config.password)
        put("database.dbname", config.database)
        put("plugin.name", "pgoutput")  // or decoderbufs
        put("slot.name", "airbyte_slot")
        put("publication.name", "airbyte_publication")
        put("snapshot.mode", "initial")
    }
}
```

**MySQL:**
```kotlin
fun mysqlDebeziumProperties(config: MySqlConfig): Properties {
    return Properties().apply {
        put("connector.class", "io.debezium.connector.mysql.MySqlConnector")
        put("database.hostname", config.host)
        put("database.port", config.port.toString())
        put("database.user", config.username)
        put("database.password", config.password)
        put("database.server.id", generateServerId())
        put("database.include.list", config.database)
        put("snapshot.mode", "initial")
        put("include.schema.changes", "false")
    }
}
```

### CDC Position Extraction

**Postgres:**
```kotlin
fun extractPostgresPosition(record: SourceRecord): PostgresCdcPosition {
    val source = record.sourceOffset()
    return PostgresCdcPosition(
        lsn = source["lsn"] as Long,
        transactionId = source["txId"] as? Long,
    )
}
```

**MySQL:**
```kotlin
fun extractMysqlPosition(record: SourceRecord): MySqlCdcPosition {
    val source = record.sourceOffset()
    return MySqlCdcPosition(
        binlogFile = source["file"] as String,
        binlogPosition = source["pos"] as Long,
        gtidSet = source["gtid"] as? String,
    )
}
```

### CDC Record Conversion

```kotlin
fun cdcRecordToAirbyte(
    record: SourceRecord,
    stream: StreamDescriptor,
): AirbyteRecordMessage {
    val value = record.value() as Struct
    val operation = value.getString("op")  // c=create, u=update, d=delete

    val data = when (operation) {
        "d" -> value.getStruct("before")  // DELETE: use before image
        else -> value.getStruct("after")  // INSERT/UPDATE: use after image
    }

    val json = structToJson(data)

    // Add CDC metadata
    json.put("_ab_cdc_cursor", extractPosition(record).toNumeric())
    if (operation == "d") {
        json.put("_ab_cdc_deleted_at", Instant.now().toString())
    }

    return AirbyteRecordMessage()
        .withStream(stream.name)
        .withNamespace(stream.namespace)
        .withData(json)
        .withEmittedAt(Instant.now().toEpochMilli())
}
```

---

## State Checkpointing

### When to Emit State

```kotlin
class StateEmissionStrategy(
    private val recordInterval: Int = 10000,
    private val timeIntervalMs: Long = 60000,
) {
    private var recordCount = 0
    private var lastEmitTime = System.currentTimeMillis()

    fun shouldEmitState(): Boolean {
        recordCount++
        val now = System.currentTimeMillis()

        return when {
            recordCount >= recordInterval -> {
                recordCount = 0
                lastEmitTime = now
                true
            }
            now - lastEmitTime >= timeIntervalMs -> {
                recordCount = 0
                lastEmitTime = now
                true
            }
            else -> false
        }
    }
}
```

### State Serialization

```kotlin
// Cursor-based state
fun serializeCursorState(
    stream: ConfiguredAirbyteStream,
    cursorValue: Any?,
): JsonNode {
    return objectMapper.valueToTree(mapOf(
        "state_type" to "cursor-based",
        "cursor_field" to stream.cursorField,
        "cursor" to cursorValue?.toString(),
    ))
}

// CDC state
fun serializeCdcState(position: CdcPosition): JsonNode {
    return when (position) {
        is PostgresCdcPosition -> objectMapper.valueToTree(mapOf(
            "lsn" to position.lsn,
            "txId" to position.transactionId,
        ))
        is MySqlCdcPosition -> objectMapper.valueToTree(mapOf(
            "file" to position.binlogFile,
            "pos" to position.binlogPosition,
            "gtid" to position.gtidSet,
        ))
    }
}
```

---

## Common Operations Reference

### Discovery SQL

**List Tables:**
```sql
-- PostgreSQL
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema');

-- MySQL
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('information_schema', 'mysql', 'performance_schema');
```

**List Columns:**
```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = ? AND table_name = ?
ORDER BY ordinal_position;
```

**Get Primary Keys:**
```sql
-- PostgreSQL
SELECT a.attname
FROM pg_index i
JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
WHERE i.indrelid = ?::regclass AND i.indisprimary;

-- MySQL
SELECT column_name
FROM information_schema.key_column_usage
WHERE table_schema = ? AND table_name = ?
  AND constraint_name = 'PRIMARY'
ORDER BY ordinal_position;
```

### Connection Validation (Check)

```kotlin
fun checkConnection(config: MySourceConfiguration): AirbyteConnectionStatus {
    return try {
        DriverManager.getConnection(
            config.toJdbcUrl(),
            config.toJdbcProperties()
        ).use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery("SELECT 1").use { rs ->
                    if (rs.next()) {
                        AirbyteConnectionStatus()
                            .withStatus(Status.SUCCEEDED)
                    } else {
                        throw RuntimeException("SELECT 1 returned no rows")
                    }
                }
            }
        }
    } catch (e: Exception) {
        AirbyteConnectionStatus()
            .withStatus(Status.FAILED)
            .withMessage(classifyError(e))
    }
}
```

---

## Quick Reference Tables

### Error Classification

| Error Pattern | SQL State | Type | Message |
|--------------|-----------|------|---------|
| Access denied | 28000, 28P01 | CONFIG | Check credentials |
| Database not found | 3D000 | CONFIG | Check database name |
| Permission denied | 42501 | CONFIG | Grant SELECT privilege |
| Connection refused | 08001, 08006 | TRANSIENT | Will retry |
| Timeout | 08000 | TRANSIENT | Will retry |
| Unknown | * | SYSTEM | Unexpected error |

### Sync Mode Selection

| User Selection | Has Cursor | CDC Enabled | Result |
|----------------|------------|-------------|--------|
| Full Refresh | - | - | Full table scan |
| Incremental | Yes | No | Cursor-based |
| Incremental | No | No | Full refresh (no cursor) |
| Incremental | - | Yes | CDC streaming |

### State Types

| Sync Mode | State Type | State Content |
|-----------|------------|---------------|
| Full Refresh | STREAM | `{}` or PK checkpoint |
| Incremental | STREAM | `{cursor_field, cursor}` |
| CDC | GLOBAL | `{shared_state: cdc_position, stream_states: [...]}` |

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Database type enum
- [ ] Configuration spec
- [ ] Configuration factory
- [ ] JDBC connection setup

### Phase 2: Discovery
- [ ] Metadata querier (tables, columns, PKs)
- [ ] Type mapping (DB types -> Airbyte types)
- [ ] Catalog builder

### Phase 3: Reading
- [ ] Source operations (ResultSet -> JSON)
- [ ] Query generation
- [ ] Full refresh implementation
- [ ] Streaming result sets

### Phase 4: Incremental
- [ ] Cursor-based queries
- [ ] State serialization
- [ ] State restoration
- [ ] Checkpoint emission

### Phase 5: CDC (Optional)
- [ ] Debezium properties
- [ ] Position extraction
- [ ] Record conversion
- [ ] CDC meta-fields
- [ ] Snapshot + streaming coordination

### Phase 6: Error Handling
- [ ] Exception classification
- [ ] Actionable error messages
- [ ] Transient error identification

### Phase 7: Testing
- [ ] Unit tests for type mapping
- [ ] Integration tests with Testcontainers
- [ ] Full refresh test
- [ ] Incremental test
- [ ] CDC test (if applicable)
