/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.integrations.destination.snowflake.dataflow.SnowflakeAggregate
import io.airbyte.integrations.destination.snowflake.db.ColumnDefinition
import io.airbyte.integrations.destination.snowflake.db.escapeJsonIdentifier
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
import io.airbyte.integrations.destination.snowflake.sql.andLog
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.time.format.DateTimeFormatter
import javax.sql.DataSource
import net.snowflake.client.jdbc.SnowflakeSQLException
import net.snowflake.client.jdbc.SnowflakeTimestampWithTimezone

internal const val DESCRIBE_TABLE_COLUMN_NAME_FIELD = "column_name"
internal const val DESCRIBE_TABLE_COLUMN_TYPE_FIELD = "data_type"

private val log = KotlinLogging.logger {}

@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "kotlin coroutines")
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
    private val snowflakeConfiguration: SnowflakeConfiguration,
) : TableOperationsClient, TableSchemaEvolutionClient {

    private val airbyteColumnNames =
        snowflakeColumnUtils.getFormattedDefaultColumnNames(false).toSet()

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            dataSource.connection.use { connection ->
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
        } catch (e: SnowflakeSQLException) {
            log.debug(e) {
                "Table ${tableName.toPrettyString()} does not exist.  Returning a null count to signal a missing table."
            }
            null
        }

    /**
     * TEST ONLY. We have a much more performant implementation in
     * [io.airbyte.integrations.destination.snowflake.db.SnowflakeDirectLoadDatabaseInitialStatusGatherer]
     * .
     */
    override suspend fun tableExists(table: TableName) = countTable(table) != null

    override suspend fun namespaceExists(namespace: String): Boolean {
        return dataSource.connection.use { connection ->
            val databaseName = snowflakeConfiguration.database.toSnowflakeCompatibleName()
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

    override suspend fun dropNamespace(namespace: String) {
        execute(sqlGenerator.dropNamespace(namespace))
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        execute(sqlGenerator.createTable(stream, tableName, columnNameMapping, replace))
        execute(sqlGenerator.createSnowflakeStage(tableName))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // Check if the target table exists by trying to count its rows
        val targetExists = countTable(targetTableName) != null

        log.info {
            "overwriteTable: source=${sourceTableName.toPrettyString()}, target=${targetTableName.toPrettyString()}, targetExists=$targetExists"
        }

        if (targetExists) {
            // If target exists, use SWAP for efficiency
            log.info { "Using SWAP operation since target table exists" }
            execute(sqlGenerator.swapTableWith(sourceTableName, targetTableName))
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
        execute(sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(
            sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)
        )
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        execute(sqlGenerator.createSnowflakeStage(tableName))
        /*
         * If legacy raw tables are in use, there is nothing to ensure in schema, as raw mode
         * uses a fixed schema that is not based on the catalog/incoming record.  Otherwise,
         * ensure that the destination schema is in sync with any changes.
         */
        if (snowflakeConfiguration.legacyRawTablesOnly) {
            return
        }
        val columnsInDb = getColumnsFromDb(tableName)
        val columnsInStream = getColumnsFromStream(stream, columnNameMapping)
        val (addedColumns, deletedColumns, modifiedColumns) =
            generateSchemaChanges(columnsInDb, columnsInStream)

        if (
            addedColumns.isNotEmpty() || deletedColumns.isNotEmpty() || modifiedColumns.isNotEmpty()
        ) {
            log.info { "Summary of the table alterations:" }
            log.info { "Added columns: $addedColumns" }
            log.info { "Deleted columns: $deletedColumns" }
            log.info { "Modified columns: $modifiedColumns" }
            sqlGenerator
                .alterTable(tableName, addedColumns, deletedColumns, modifiedColumns)
                .forEach { execute(it) }
        }
    }

    internal fun getColumnsFromDb(tableName: TableName): Set<ColumnDefinition> {
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
                    val columnsInDb: MutableSet<ColumnDefinition> = mutableSetOf()

                    while (rs.next()) {
                        val columnName = escapeJsonIdentifier(rs.getString("name"))

                        // Filter out airbyte columns
                        if (airbyteColumnNames.contains(columnName)) {
                            continue
                        }
                        val dataType = rs.getString("type").takeWhile { char -> char != '(' }

                        columnsInDb.add(ColumnDefinition(columnName, dataType, false))
                    }

                    columnsInDb
                }
            }
        } catch (e: SnowflakeSQLException) {
            handleSnowflakePermissionError(e)
        }
    }

    internal fun getColumnsFromStream(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ) =
        snowflakeColumnUtils
            .columnsAndTypes(stream.schema.asColumns(), columnNameMapping)
            .filter { column -> column.columnName !in airbyteColumnNames }
            .map { column ->
                ColumnDefinition(
                    name = column.columnName,
                    type =
                        column.columnType.takeWhile { char ->
                            // This is to remove any precision parts of the dialect type
                            char != '('
                        },
                    // Not used to ensure schema
                    isPrimaryKey = false,
                )
            }
            .toSet()

    internal fun generateSchemaChanges(
        columnsInDb: Set<ColumnDefinition>,
        columnsInStream: Set<ColumnDefinition>
    ): Triple<Set<ColumnDefinition>, Set<ColumnDefinition>, Set<ColumnDefinition>> {
        val addedColumns =
            columnsInStream.filter { it.name !in columnsInDb.map { col -> col.name } }.toSet()
        val deletedColumns =
            columnsInDb.filter { it.name !in columnsInStream.map { col -> col.name } }.toSet()
        val commonColumns =
            columnsInStream.filter { it.name in columnsInDb.map { col -> col.name } }.toSet()
        val modifiedColumns =
            commonColumns
                .filter {
                    val dbType = columnsInDb.find { column -> it.name == column.name }?.type
                    it.type != dbType
                }
                .toSet()
        return Triple(addedColumns, deletedColumns, modifiedColumns)
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
                        resultSet.getLong(snowflakeColumnUtils.getGenerationIdColumnName())
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

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        val a =
            SnowflakeAggregate(
                SnowflakeInsertBuffer(
                    table,
                    describeTable(table),
                    this,
                    snowflakeConfiguration,
                    snowflakeColumnUtils,
                )
            )
        records.forEach { a.accept(RecordDTO(it, PartitionKey(""), 0, 0)) }
        a.flush()
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement
                    .executeQuery("""SELECT * FROM "${table.namespace}"."${table.name}";""")
                    .use { resultSet ->
                        val metaData = resultSet.metaData
                        val columnCount = metaData.columnCount
                        val result = mutableListOf<Map<String, Any>>()

                        while (resultSet.next()) {
                            val row = mutableMapOf<String, Any>()
                            for (i in 1..columnCount) {
                                val columnName = metaData.getColumnName(i)
                                val columnType = metaData.getColumnTypeName(i)
                                when (columnType) {
                                    "TIMESTAMPTZ" -> {
                                        val value =
                                            resultSet.getTimestamp(i)
                                                as SnowflakeTimestampWithTimezone?
                                        value?.let {
                                            val formattedTimestamp =
                                                DateTimeFormatter.ISO_DATE_TIME.format(
                                                    it.toZonedDateTime().toOffsetDateTime()
                                                )
                                            row[columnName] = formattedTimestamp
                                        }
                                    }
                                    "VARIANT",
                                    "OBJECT",
                                    "ARRAY" -> {
                                        resultSet.getString(i)?.let {
                                            // Automatically convert values to their native type.
                                            // (map, list, etc.)
                                            val parsedValue = Jsons.readValue(it, Any::class.java)
                                            // but handle some annoying edge cases
                                            val actualValue =
                                                when (parsedValue) {
                                                    is Int -> parsedValue.toLong()
                                                    else -> parsedValue
                                                }
                                            row[columnName] = actualValue
                                        }
                                    }
                                    else -> {
                                        resultSet.getObject(i)?.let { row[columnName] = it }
                                    }
                                }
                            }
                            result.add(row)
                        }

                        return result
                    }
            }
        }
    }

    fun createSnowflakeStage(tableName: TableName) {
        execute(sqlGenerator.createSnowflakeStage(tableName))
    }

    fun putInStage(tableName: TableName, tempFilePath: String) {
        execute(sqlGenerator.putInStage(tableName, tempFilePath))
    }

    fun copyFromStage(tableName: TableName, filename: String) {
        execute(sqlGenerator.copyFromStage(tableName, filename))
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

    internal fun execute(query: String) =
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { it.executeQuery(query) }
            }
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
