/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.client

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.starrocks.schema.StarrocksSqlTypes
import io.airbyte.integrations.destination.starrocks.spec.StarrocksConfiguration
import io.airbyte.integrations.destination.starrocks.sql.KeyModel
import io.airbyte.integrations.destination.starrocks.sql.StarrocksColumn
import io.airbyte.integrations.destination.starrocks.sql.StarrocksSqlGenerator
import io.airbyte.integrations.destination.starrocks.sql.quoteIdent
import io.airbyte.integrations.destination.starrocks.tunnel.StarrocksSshTunnel
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.DriverManager
import java.time.Duration
import java.util.UUID
import kotlinx.coroutines.delay

private val log = KotlinLogging.logger {}

/**
 * Append/Overwrite -> DUPLICATE KEY (StarRocks keeps every row; a DUPLICATE key is NOT a uniqueness
 * constraint, and the key is the per-record unique `_airbyte_raw_id`, so append never collapses
 * business-duplicate records). Dedupe -> PRIMARY KEY (StarRocks upserts/deletes by key at load time
 * via `__op`). This is the guard against accidental dedup of append data.
 */
internal fun keyModelFor(importType: ImportType): KeyModel =
    if (importType is Dedupe) KeyModel.PRIMARY else KeyModel.DUPLICATE

/**
 * Maps an `information_schema.columns.DATA_TYPE` value (lowercase, length stripped) back to the
 * connector's canonical StarRocks type literal, so [StarrocksAirbyteClient.discoverSchema] compares
 * equal to the mapper's output. Without this, a second sync sees every column as "changed" (e.g.
 * discovered `bigint` vs canonical `BIGINT`) and tries to `ALTER ... MODIFY` the PRIMARY KEY
 * columns, which StarRocks rejects ("Can not modify key column ... for primary key table").
 */
internal fun canonicalStarrocksType(dataType: String): String =
    when (dataType.lowercase().substringBefore('(').trim()) {
        "boolean" -> StarrocksSqlTypes.BOOLEAN
        "bigint" -> StarrocksSqlTypes.BIGINT
        "decimal",
        "decimalv2",
        "decimalv3",
        "decimal32",
        "decimal64",
        "decimal128" -> StarrocksSqlTypes.DECIMAL
        "date" -> StarrocksSqlTypes.DATE
        "datetime" -> StarrocksSqlTypes.DATETIME
        "varchar",
        "char",
        "string" -> StarrocksSqlTypes.STRING
        "json" -> StarrocksSqlTypes.JSON
        else -> dataType.uppercase()
    }

/**
 * Adjusts the desired columns for a schema-evolution rebuild so the copy can't fail on the #77
 * nullability rule. StarRocks cannot store NULL in a `NOT NULL` column, and schema-evolution-added
 * columns are kept NULLABLE; so a NON-key column that is currently nullable but whose desired type
 * is `NOT NULL` is kept NULLABLE in the rebuilt table (existing rows may hold NULLs). Key columns
 * are always `NOT NULL` (enforced by `createTable`) and are left untouched.
 */
internal fun rebuildColumns(
    columns: List<StarrocksColumn>,
    keyColumns: Set<String>,
    columnChangeset: ColumnChangeset,
): List<StarrocksColumn> =
    columns.map { col ->
        val change = columnChangeset.columnsToChange[col.name]
        if (
            change != null &&
                change.originalType.nullable &&
                !col.nullable &&
                col.name !in keyColumns
        ) {
            col.copy(nullable = true)
        } else {
            col
        }
    }

/**
 * Builds the `INSERT INTO <temp> SELECT ... FROM <real>` that re-populates a rebuilt table (#70).
 * Each desired column is sourced from the existing table by name: a type-changed column is `CAST`
 * to its new type (lossless for widenings like `BIGINT`->`DECIMAL`), a freshly added column has no
 * source value so it is `NULL`, and everything else — including the meta columns, which never
 * appear in the changeset — is copied verbatim. Dropped columns are simply absent from [columns].
 */
internal fun rebuildInsertSql(
    qualifiedTemp: String,
    qualifiedReal: String,
    columns: List<StarrocksColumn>,
    columnChangeset: ColumnChangeset,
): String {
    val colList = columns.joinToString(", ") { quoteIdent(it.name) }
    val selectList =
        columns.joinToString(", ") { col ->
            when (col.name) {
                in columnChangeset.columnsToAdd -> "NULL"
                in columnChangeset.columnsToChange ->
                    "CAST(${quoteIdent(col.name)} AS ${col.sqlType})"
                else -> quoteIdent(col.name)
            }
        }
    return "INSERT INTO $qualifiedTemp ($colList) SELECT $selectList FROM $qualifiedReal"
}

/**
 * StarRocks implementation of the CDK [TableOperationsClient] / [TableSchemaEvolutionClient]. All
 * DDL and table metadata run over the MySQL protocol (port 9030). High-volume row writes do NOT go
 * through here — they use Stream Load over HTTP (see the dataflow Aggregate). This mirrors
 * `ClickhouseAirbyteClient`, adapted to StarRocks SQL.
 *
 * Deduplication is performed at load time via the `__op` column into a PRIMARY KEY table, so the
 * server-side [upsertTable] merge that ClickHouse leaves to its engine is likewise unimplemented
 * here.
 */
@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class StarrocksAirbyteClient(
    private val config: StarrocksConfiguration,
    private val sqlGenerator: StarrocksSqlGenerator,
    private val tunnel: StarrocksSshTunnel,
) : TableOperationsClient, TableSchemaEvolutionClient {

    // When tunneling, connect to the SSH local forward; otherwise straight to StarRocks (#68).
    private val jdbcUrl: String = config.jdbcUrlFor(tunnel.jdbcHost, tunnel.jdbcPort)

    private fun <T> withConnection(block: (Connection) -> T): T =
        DriverManager.getConnection(jdbcUrl, config.username, config.password).use(block)

    private fun execute(sql: String) {
        log.info { sql }
        withConnection { conn -> conn.createStatement().use { it.execute(sql) } }
    }

    /**
     * StarRocks server version (`SELECT current_version()`), read once and cached. Used at write
     * start to opt into version-gated Stream Load capabilities (see [StarrocksVersionGate]);
     * `check` reads it separately for fail-fast validation.
     */
    private val cachedVersion: String by lazy {
        withConnection { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery("SELECT current_version()").use { rs ->
                    if (rs.next()) rs.getString(1).orEmpty() else ""
                }
            }
        }
    }

    fun serverVersion(): String = cachedVersion

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createDatabase(namespace))
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        if (replace) {
            execute(sqlGenerator.dropTable(tableName.namespace, tableName.name))
        }
        val (columns, keyColumns, model) = describeTable(stream.tableSchema)
        execute(
            sqlGenerator.createTable(
                database = tableName.namespace,
                table = tableName.name,
                columns = columns,
                keyColumns = keyColumns,
                model = model,
                // When replacing we just dropped the table; otherwise keep it idempotent.
                ifNotExists = !replace,
                replicationNum = config.replicationNum,
            ),
        )
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName.namespace, tableName.name))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // StarRocks atomically swaps the two tables' data/schema; the SWAP WITH operand must be an
        // unqualified name (same database). We then drop the (now-source) leftover.
        execute(
            sqlGenerator.swapTable(
                targetTableName.namespace,
                targetTableName.name,
                sourceTableName.name,
            ),
        )
        execute(sqlGenerator.dropTable(sourceTableName.namespace, sourceTableName.name))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        val cols = (META_COLUMNS + columnNameMapping.values).joinToString(", ") { quoteIdent(it) }
        execute(
            "INSERT INTO ${quoteIdent(targetTableName.namespace)}.${quoteIdent(targetTableName.name)} ($cols) " +
                "SELECT $cols FROM ${quoteIdent(sourceTableName.namespace)}.${quoteIdent(sourceTableName.name)}",
        )
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        // StarRocks deduplicates at LOAD time (`__op` into a PRIMARY KEY table), so there is no
        // server-side temp->real merge step to implement.
        throw NotImplementedError(
            "StarRocks deduplicates at load time via __op into a PRIMARY KEY table"
        )
    }

    override suspend fun namespaceExists(namespace: String): Boolean = withConnection { conn ->
        conn
            .prepareStatement(
                "SELECT SCHEMA_NAME FROM information_schema.schemata WHERE SCHEMA_NAME = ?",
            )
            .use { ps ->
                ps.setString(1, namespace)
                ps.executeQuery().use { it.next() }
            }
    }

    override suspend fun tableExists(table: TableName): Boolean = withConnection { conn ->
        conn
            .prepareStatement(
                "SELECT TABLE_NAME FROM information_schema.tables " +
                    "WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?",
            )
            .use { ps ->
                ps.setString(1, table.namespace)
                ps.setString(2, table.name)
                ps.executeQuery().use { it.next() }
            }
    }

    // A genuinely missing table is reported as null ("absent") via the explicit existence check;
    // any other (connection/auth/query) error propagates rather than being silently swallowed
    // (#42).
    override suspend fun countTable(tableName: TableName): Long? {
        if (!tableExists(tableName)) return null
        return withConnection { conn ->
            conn.createStatement().use { stmt ->
                stmt
                    .executeQuery(
                        "SELECT count(1) FROM ${quoteIdent(tableName.namespace)}.${quoteIdent(tableName.name)}",
                    )
                    .use { rs -> if (rs.next()) rs.getLong(1) else null }
            }
        }
    }

    // MAX (not LIMIT 1 without ORDER BY) so the generation id is deterministic even when the table
    // holds rows from multiple generations (#41). Missing table -> 0L; other errors propagate
    // (#42).
    override suspend fun getGenerationId(tableName: TableName): Long {
        if (!tableExists(tableName)) return 0L
        return withConnection { conn ->
            conn.createStatement().use { stmt ->
                stmt
                    .executeQuery(
                        "SELECT MAX(${quoteIdent(COLUMN_NAME_AB_GENERATION_ID)}) " +
                            "FROM ${quoteIdent(tableName.namespace)}.${quoteIdent(tableName.name)}",
                    )
                    .use { rs -> if (rs.next()) rs.getLong(1) else 0L }
            }
        }
    }

    override suspend fun discoverSchema(tableName: TableName): TableSchema =
        withConnection { conn ->
            val columns = LinkedHashMap<String, ColumnType>()
            conn
                .prepareStatement(
                    "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM information_schema.columns " +
                        "WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?",
                )
                .use { ps ->
                    ps.setString(1, tableName.namespace)
                    ps.setString(2, tableName.name)
                    ps.executeQuery().use { rs ->
                        while (rs.next()) {
                            val name = rs.getString("COLUMN_NAME")
                            if (name in META_COLUMNS) continue
                            val type = rs.getString("DATA_TYPE")
                            val nullable =
                                rs.getString("IS_NULLABLE").equals("YES", ignoreCase = true)
                            columns[name] = ColumnType(canonicalStarrocksType(type), nullable)
                        }
                    }
                }
            TableSchema(columns)
        }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
    ): TableSchema = TableSchema(stream.tableSchema.columnSchema.finalSchema)

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: Map<String, ColumnType>,
        columnChangeset: ColumnChangeset,
    ) {
        // Explicit emptiness check rather than ColumnChangeset.isNoop(): since load CDK 1.0.17
        // isNoop() ignores columnsToDrop, which would silently turn a drop-only changeset into a
        // no-op. This connector applies documented in-place drops (non-key columns).
        if (
            columnChangeset.columnsToAdd.isEmpty() &&
                columnChangeset.columnsToDrop.isEmpty() &&
                columnChangeset.columnsToChange.isEmpty()
        )
            return

        // A type/nullability change often can't be applied in place — StarRocks rejects many ALTER
        // MODIFYs (e.g. BIGINT->DECIMAL for integer->number). Rather than
        // skip-and-silently-truncate,
        // REBUILD: create a temp with the desired schema, INSERT...SELECT CAST the data, then
        // atomically
        // SWAP. This applies adds/drops/changes together and is lossless for widenings — mirroring
        // how
        // BigQuery/Snowflake handle a destination that can't ALTER a column type in place (#70).
        if (columnChangeset.columnsToChange.isNotEmpty()) {
            rebuildTable(stream, tableName, columnChangeset)
            return
        }

        // No type changes: cheap in-place ADD/DROP (metadata-only on shared-data fast schema
        // evolution). All clauses go out as ONE ALTER statement: StarRocks runs each ALTER as an
        // async schema-change job and rejects a second ALTER on the table while the first is still
        // in flight ("A schema change operation is in progress"), which a per-column ALTER loop hit
        // live on a 4.0 shared-data cluster.
        val addColumns =
            columnChangeset.columnsToAdd.map { (name, type) ->
                // New columns are always added NULLABLE: StarRocks rejects `ADD COLUMN ... NOT
                // NULL`
                // without a DEFAULT on a populated table, and existing rows have no value for a
                // freshly added column anyway (so they must be null) (#43).
                if (!type.nullable) {
                    log.warn {
                        "Adding column `$name` as NULLABLE — StarRocks cannot ADD a NOT NULL column to an existing table"
                    }
                }
                StarrocksColumn(name, type.type, nullable = true)
            }
        // #70 Gap A (deferred — intentionally not guarded): if a dropped column is a PRIMARY KEY
        // column (the source dropped/renamed its PK), StarRocks rejects this ("Can not drop key
        // column in primary data model table") and the sync fails. The real fix is a table
        // recreation, which Airbyte gates behind a manual Refresh (a PK removal is a breaking
        // change → the connection pauses for review). Revisit only to surface a clearer error than
        // the raw 1064.
        val dropColumns = columnChangeset.columnsToDrop.keys.toList()
        execute(
            sqlGenerator.alterTableColumns(
                tableName.namespace,
                tableName.name,
                addColumns,
                dropColumns
            ),
        )
        awaitSchemaChange(tableName)
    }

    /**
     * Waits for the most recent schema-change job on [tableName] to finish. StarRocks applies
     * `ALTER TABLE ... COLUMN` asynchronously: the statement returns while the job is still
     * PENDING/RUNNING. Loads against the table succeed meanwhile, but the next ALTER on it (the
     * next sync's evolution) is rejected with "A schema change operation is in progress", and
     * `information_schema.columns` may still show the old shape. On shared-data clusters this
     * finishes within seconds; the bound turns a stuck job into a loud failure instead of a hang.
     */
    internal suspend fun awaitSchemaChange(tableName: TableName) {
        val deadline = System.nanoTime() + SCHEMA_CHANGE_TIMEOUT.toNanos()
        while (true) {
            val (state, msg) = latestSchemaChange(tableName) ?: return
            when (state) {
                "FINISHED" -> return
                "CANCELLED" ->
                    throw IllegalStateException(
                        "Schema change on ${tableName.namespace}.${tableName.name} was cancelled by StarRocks: $msg"
                    )
            }
            check(System.nanoTime() < deadline) {
                "Schema change on ${tableName.namespace}.${tableName.name} still $state after " +
                    "${SCHEMA_CHANGE_TIMEOUT.toMinutes()} min; see SHOW ALTER TABLE COLUMN"
            }
            delay(SCHEMA_CHANGE_POLL.toMillis())
        }
    }

    /** (State, Msg) of the latest schema-change job on the table, or null if it never had one. */
    private fun latestSchemaChange(tableName: TableName): Pair<String, String>? =
        withConnection { conn ->
            conn.createStatement().use { stmt ->
                stmt
                    .executeQuery(
                        sqlGenerator.showLatestSchemaChange(tableName.namespace, tableName.name)
                    )
                    .use { rs ->
                        if (rs.next()) rs.getString("State") to (rs.getString("Msg") ?: "")
                        else null
                    }
            }
        }

    /**
     * Rebuilds [tableName] to the stream's desired schema when a type/nullability change can't be
     * ALTERed in place (#70): create a temp table with the new schema, copy the data through
     * per-column `CAST`s (lossless for widenings; added columns become NULL, dropped columns are
     * omitted), then atomically `SWAP WITH` and drop the leftover. Mirrors the BigQuery/Snowflake
     * rebuild approach; the real table is untouched until the SWAP, so a mid-rebuild failure leaves
     * the data intact.
     */
    private suspend fun rebuildTable(
        stream: DestinationStream,
        tableName: TableName,
        columnChangeset: ColumnChangeset,
    ) {
        val (columns, keyColumns, model) = describeTable(stream.tableSchema)
        val rebuilt = rebuildColumns(columns, keyColumns.toSet(), columnChangeset)
        val db = tableName.namespace
        val tempTable = "${tableName.name}_ab_evo_${UUID.randomUUID().toString().replace("-", "")}"
        log.info {
            "Rebuilding ${quoteIdent(db)}.${quoteIdent(tableName.name)} (via $tempTable) to apply " +
                "${columnChangeset.columnsToChange.size} type change(s) StarRocks can't ALTER in place (#70)"
        }
        execute(
            sqlGenerator.createTable(
                database = db,
                table = tempTable,
                columns = rebuilt,
                keyColumns = keyColumns,
                model = model,
                ifNotExists = false,
                replicationNum = config.replicationNum,
            ),
        )
        execute(
            rebuildInsertSql(
                "${quoteIdent(db)}.${quoteIdent(tempTable)}",
                "${quoteIdent(db)}.${quoteIdent(tableName.name)}",
                rebuilt,
                columnChangeset,
            ),
        )
        execute(sqlGenerator.swapTable(db, tableName.name, tempTable))
        execute(sqlGenerator.dropTable(db, tempTable))
    }

    /**
     * Resolves a [StreamTableSchema] into the StarRocks (columns, keyColumns, model) needed by the
     * SQL generator. Adds the four Airbyte meta columns and chooses the key model: Dedupe ->
     * PRIMARY on the stream PK; else DUPLICATE on `_airbyte_raw_id`.
     */
    private fun describeTable(
        tableSchema: StreamTableSchema,
    ): Triple<List<StarrocksColumn>, List<String>, KeyModel> {
        val metaColumns =
            listOf(
                StarrocksColumn(COLUMN_NAME_AB_RAW_ID, StarrocksSqlTypes.STRING, nullable = false),
                StarrocksColumn(
                    COLUMN_NAME_AB_EXTRACTED_AT,
                    StarrocksSqlTypes.DATETIME,
                    nullable = false
                ),
                StarrocksColumn(COLUMN_NAME_AB_META, StarrocksSqlTypes.STRING, nullable = false),
                StarrocksColumn(
                    COLUMN_NAME_AB_GENERATION_ID,
                    StarrocksSqlTypes.BIGINT,
                    nullable = false
                ),
            )
        val userColumns =
            tableSchema.columnSchema.finalSchema.map { (name, type) ->
                StarrocksColumn(name, type.type, type.nullable)
            }

        val importType = tableSchema.importType
        val keyColumns =
            if (importType is Dedupe) importType.primaryKey.map { it.single() }
            else listOf(COLUMN_NAME_AB_RAW_ID)
        return Triple(metaColumns + userColumns, keyColumns, keyModelFor(importType))
    }

    companion object {
        private val SCHEMA_CHANGE_POLL: Duration = Duration.ofSeconds(1)
        private val SCHEMA_CHANGE_TIMEOUT: Duration = Duration.ofMinutes(10)
        private val META_COLUMNS =
            listOf(
                COLUMN_NAME_AB_RAW_ID,
                COLUMN_NAME_AB_EXTRACTED_AT,
                COLUMN_NAME_AB_META,
                COLUMN_NAME_AB_GENERATION_ID,
            )
    }
}
