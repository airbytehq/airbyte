/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
import io.airbyte.integrations.destination.snowflake.sql.andLog
import io.airbyte.integrations.destination.snowflake.sql.escapeJsonIdentifier
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.util.concurrent.ConcurrentHashMap
import javax.sql.DataSource
import net.snowflake.client.jdbc.SnowflakeSQLException

internal const val DESCRIBE_TABLE_COLUMN_NAME_FIELD = "column_name"
internal const val DESCRIBE_TABLE_COLUMN_TYPE_FIELD = "data_type"

private val log = KotlinLogging.logger {}

@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "kotlin coroutines")
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val columnManager: SnowflakeColumnManager,
) : TableOperationsClient, TableSchemaEvolutionClient {
    private val databaseName = snowflakeConfiguration.database.toSnowflakeCompatibleName()

    private data class PendingTempTable(
        val schema: StreamTableSchema,
        val replace: Boolean,
    )

    /**
     * Temporary tables are registered here and materialized by the first write. This avoids
     * creating a table and stage for a stream that receives no records.
     *
     * Each value also acts as that table's initialization lock. It is deliberately removed only
     * after both CREATE TABLE and CREATE STAGE have completed, so concurrent PUTs cannot race ahead
     * of stage creation.
     */
    private val pendingTempTables = ConcurrentHashMap<TableName, PendingTempTable>()

    override suspend fun countTable(tableName: TableName): Long? {
        return getTableRowCount(tableName)
    }

    /** Used by CHECK, where the exact post-write count is part of the connectivity assertion. */
    fun exactCountTable(tableName: TableName): Long {
        return dataSource.connection.use { connection ->
            val statement = connection.createStatement()
            statement.use {
                val resultSet = it.executeQuery(sqlGenerator.countTable(tableName))

                if (resultSet.next()) {
                    resultSet.getLong(COUNT_TOTAL_ALIAS)
                } else {
                    0L
                }
            }
        }
    }

    override suspend fun tableExists(table: TableName): Boolean = getTableRowCount(table) != null

    /**
     * Reads Snowflake's table metadata rather than executing SELECT COUNT(*). Initial status only
     * needs to distinguish missing, empty, and non-empty tables; it does not need an exact count.
     */
    private fun getTableRowCount(table: TableName): Long? =
        dataSource.connection.use { connection ->
            val statement =
                connection.prepareStatement(
                    """
                    show tables
                    like ?
                    in schema "$databaseName"."${table.namespace}"
                    """.trimIndent()
                )
            statement.setString(1, table.name)
            statement.use {
                val resultSet = it.executeQuery()
                if (resultSet.next()) resultSet.getLong("rows") else null
            }
        }

    override suspend fun namespaceExists(namespace: String): Boolean {
        return dataSource.connection.use { connection ->
            val statement =
                connection.prepareStatement(
                    """
                        SELECT COUNT(*) > 0 AS SCHEMA_EXISTS
                        FROM "$databaseName".INFORMATION_SCHEMA.SCHEMATA
                        WHERE SCHEMA_NAME = ?
                    """.andLog()
                )

            // When querying information_schema, snowflake needs the "true" schema name,
            // so we unescape it here.
            val unescapedNamespace = namespace.replace("\"\"", "\"")
            statement.setString(1, unescapedNamespace)

            statement.use {
                val resultSet = it.executeQuery()
                resultSet.use { rs ->
                    if (rs.next()) {
                        rs.getBoolean("SCHEMA_EXISTS")
                    } else {
                        false
                    }
                }
            }
        }
    }

    override suspend fun createNamespace(namespace: String) {
        try {
            // Check if the schema exists first
            val schemaExistsResult = namespaceExists(namespace)

            if (!schemaExistsResult) {
                // Create the schema only if it doesn't exist
                execute(sqlGenerator.createNamespace(namespace))
            }
        } catch (e: SnowflakeSQLException) {
            handleSnowflakePermissionError(e)
        }
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        createTableAndStage(tableName, stream.tableSchema, replace)
    }

    override suspend fun createTempTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        pendingTempTables[tableName] = PendingTempTable(stream.tableSchema, replace)
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // Truncate/overwrite modes must still replace the target with an empty table when the
        // source emits zero records, so materialize the deferred source before overwriting.
        materializePendingTempTable(sourceTableName)

        // Check if the target table exists by trying to count its rows
        val targetExists = countTable(targetTableName) != null

        log.info {
            "overwriteTable: source=${sourceTableName.toPrettyString()}, target=${targetTableName.toPrettyString()}, targetExists=$targetExists"
        }

        if (targetExists) {
            // If target exists, use CLONE for efficiency
            log.info { "Using CLONE operation since target table exists" }
            execute(sqlGenerator.cloneTableWith(sourceTableName, targetTableName))
            execute(sqlGenerator.dropTable(sourceTableName))
        } else {
            // If target doesn't exist, rename source to target
            log.info { "Using RENAME operation since target table doesn't exist" }
            // Drop target if it somehow exists (defensive programming)
            try {
                execute(sqlGenerator.dropTable(targetTableName))
                log.info { "Dropped existing target table before rename" }
            } catch (e: Exception) {
                // Table doesn't exist, which is expected
                log.debug { "Target table doesn't exist to drop (expected): ${e.message}" }
            }
            execute(sqlGenerator.renameTable(sourceTableName, targetTableName))
        }
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        if (isPendingTempTable(sourceTableName)) {
            log.info {
                "Skipping copy from unmaterialized empty temp table ${sourceTableName.toPrettyString()}"
            }
            return
        }

        // Get all column names from the mapping (both meta columns and user columns)
        val columnNames = buildSet {
            // Add Airbyte meta columns (using uppercase constants)
            addAll(columnManager.getMetaColumnNames())
            // Add user columns from mapping
            addAll(columnNameMapping.values)
        }

        execute(sqlGenerator.copyTable(columnNames, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        if (isPendingTempTable(sourceTableName)) {
            log.info {
                "Skipping upsert from unmaterialized empty temp table ${sourceTableName.toPrettyString()}"
            }
            return
        }

        // Dedup + truncate can upsert into a second deferred temporary table. It must exist before
        // the MERGE starts whenever the source actually contains records.
        materializePendingTempTable(targetTableName)
        execute(sqlGenerator.upsertTable(stream.tableSchema, sourceTableName, targetTableName))
    }

    override suspend fun dropTable(tableName: TableName) {
        if (discardPendingTempTable(tableName)) {
            log.info {
                "Skipping drop of unmaterialized empty temp table ${tableName.toPrettyString()}"
            }
            return
        }
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        /*
         * If legacy raw tables are in use, there is nothing to ensure in schema, as raw mode
         * uses a fixed schema that is not based on the catalog/incoming record.  Otherwise,
         * ensure that the destination schema is in sync with any changes.
         */
        if (snowflakeConfiguration.legacyRawTablesOnly) {
            return
        }
        super.ensureSchemaMatches(stream, tableName, columnNameMapping)
    }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        return TableSchema(getColumnsFromDb(tableName))
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema {
        return TableSchema(stream.tableSchema.columnSchema.finalSchema)
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        if (
            columnChangeset.columnsToAdd.isNotEmpty() ||
                columnChangeset.columnsToChange.isNotEmpty()
        ) {
            log.info { "Summary of the table alterations:" }
            log.info { "Added columns: ${columnChangeset.columnsToAdd}" }
            log.info { "Modified columns: ${columnChangeset.columnsToChange}" }
            sqlGenerator
                .alterTable(
                    tableName,
                    columnChangeset.columnsToAdd,
                    columnChangeset.columnsToChange,
                )
                .forEach { execute(it) }
        }
    }

    internal fun getColumnsFromDb(tableName: TableName): Map<String, ColumnType> {
        try {
            val sql =
                sqlGenerator.describeTable(
                    schemaName = tableName.namespace,
                    tableName = tableName.name
                )
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                return statement.use {
                    val rs: ResultSet = it.executeQuery(sql)
                    val columnsInDb: MutableMap<String, ColumnType> = mutableMapOf()

                    while (rs.next()) {
                        val columnName = escapeJsonIdentifier(rs.getString("name"))

                        // Filter out airbyte columns
                        if (columnManager.getMetaColumnNames().contains(columnName)) {
                            continue
                        }
                        val dataType = rs.getString("type").takeWhile { char -> char != '(' }
                        // yes, this is how we live. The value is, in fact "Y" or "N".
                        val nullable = rs.getString("null?") == "Y"

                        columnsInDb[columnName] = ColumnType(dataType, nullable)
                    }

                    columnsInDb
                }
            }
        } catch (e: SnowflakeSQLException) {
            handleSnowflakePermissionError(e)
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    val resultSet = it.executeQuery(sqlGenerator.getGenerationId(tableName))
                    if (resultSet.next()) {
                        /*
                         * When we retrieve the column names from the database, they are in unescaped
                         * format.  In order to make sure these strings will match any column names
                         * that we have formatted in-memory, re-apply the escaping.
                         */
                        resultSet.getLong(columnManager.getGenerationIdColumnName())
                    } else {
                        log.warn {
                            "No generation ID found for table ${tableName.toPrettyString()}, returning 0"
                        }
                        0L
                    }
                }
            }
        } catch (e: Exception) {
            log.error(e) {
                "Failed to retrieve the generation ID for table ${tableName.toPrettyString()}"
            }
            // Return 0 if we can't get the generation ID (similar to ClickHouse approach)
            0L
        }

    fun createSnowflakeStage(tableName: TableName) {
        execute(sqlGenerator.createSnowflakeStage(tableName))
    }

    fun putInStage(tableName: TableName, tempFilePath: String) {
        materializePendingTempTable(tableName)
        execute(sqlGenerator.putInStage(tableName, tempFilePath))
    }

    private fun createTableAndStage(
        tableName: TableName,
        tableSchema: StreamTableSchema,
        replace: Boolean,
    ) {
        execute(sqlGenerator.createTable(tableName, tableSchema, replace))
        execute(sqlGenerator.createSnowflakeStage(tableName))
    }

    /**
     * Materializes a deferred table exactly once. Callers that arrive during initialization wait
     * for table and stage creation to finish before continuing.
     */
    private fun materializePendingTempTable(tableName: TableName): Boolean {
        val pending = pendingTempTables[tableName] ?: return false
        synchronized(pending) {
            if (pendingTempTables[tableName] !== pending) {
                return false
            }
            createTableAndStage(tableName, pending.schema, pending.replace)
            pendingTempTables.remove(tableName, pending)
            return true
        }
    }

    /** Waits for in-flight materialization before deciding whether a table is still deferred. */
    private fun isPendingTempTable(tableName: TableName): Boolean {
        val pending = pendingTempTables[tableName] ?: return false
        synchronized(pending) {
            return pendingTempTables[tableName] === pending
        }
    }

    private fun discardPendingTempTable(tableName: TableName): Boolean {
        val pending = pendingTempTables[tableName] ?: return false
        synchronized(pending) {
            return pendingTempTables.remove(tableName, pending)
        }
    }

    fun copyFromStage(tableName: TableName, filename: String, columnNames: List<String>) {
        execute(sqlGenerator.copyFromStage(tableName, filename, columnNames))
    }

    fun describeTable(tableName: TableName): LinkedHashMap<String, String> =
        try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                return statement.use {
                    val resultSet = it.executeQuery(sqlGenerator.showColumns(tableName))
                    val columns = linkedMapOf<String, String>()
                    while (resultSet.next()) {
                        val columnName = resultSet.getString(DESCRIBE_TABLE_COLUMN_NAME_FIELD)
                        // this is... incredibly annoying. The resultset will give us a string like
                        // `{"type":"VARIANT","nullable":true}`.
                        // So we need to parse that JSON, and then fetch the actual thing we care
                        // about.
                        // Also, some of the type names aren't the ones we're familiar with (e.g.
                        // `FIXED` for numeric columns),
                        // so the output here is not particularly ergonomic.
                        val columnType =
                            resultSet
                                .getString(DESCRIBE_TABLE_COLUMN_TYPE_FIELD)
                                .deserializeToNode()["type"]
                                .asText()
                        columns[columnName] = columnType
                    }
                    columns
                }
            }
        } catch (e: SnowflakeSQLException) {
            handleSnowflakePermissionError(e)
        }

    internal fun execute(query: String): ResultSet =
        try {
            dataSource.execute(query)
        } catch (e: SnowflakeSQLException) {
            handleSnowflakePermissionError(e)
        }

    /**
     * Checks if a SnowflakeSQLException is related to permissions and wraps it as a
     * ConfigErrorException. Otherwise, rethrows the original exception.
     */
    private fun handleSnowflakePermissionError(e: SnowflakeSQLException): Nothing {
        val errorMessage = e.message?.lowercase() ?: ""

        // Check for known permission-related error patterns
        when {
            errorMessage.contains("current role has no privileges on it") -> {
                throw ConfigErrorException(e.message ?: "Permission error", e)
            }
            else -> {
                // Not a known permission error, rethrow as-is
                throw e
            }
        }
    }
}

fun DataSource.execute(query: String): ResultSet =
    this.connection.use { connection ->
        connection.createStatement().use { it.executeQuery(query) }
    }
