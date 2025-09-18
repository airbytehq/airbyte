/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.snowflake.db.ColumnDefinition
import io.airbyte.integrations.destination.snowflake.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import javax.sql.DataSource
import net.snowflake.client.jdbc.SnowflakeSQLException

internal const val DESCRIBE_TABLE_COLUMN_NAME_FIELD = "column_name"

private val log = KotlinLogging.logger {}

@Singleton
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
) : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            dataSource.connection.use { connection ->
                val resultSet =
                    connection.createStatement().executeQuery(sqlGenerator.countTable(tableName))

                if (resultSet.next()) {
                    resultSet.getLong(COUNT_TOTAL_ALIAS)
                } else {
                    0L
                }
            }
        } catch (e: SnowflakeSQLException) {
            log.debug(e) {
                "Table ${tableName.toPrettyString(quote=QUOTE)} does not exist.  Returning a null count to signal a missing table."
            }
            null
        }

    override suspend fun createNamespace(namespace: String) {
        // Create the schema if it doesn't exist
        execute(sqlGenerator.createNamespace(namespace))
        // Create the CSV file format in the schema if it does not exist
        execute(sqlGenerator.createFileFormat(namespace))
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
        execute(sqlGenerator.swapTableWith(sourceTableName, targetTableName))
        execute(sqlGenerator.dropTable(sourceTableName))
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
        execute(sqlGenerator.dropStage(tableName))
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        val sql =
            sqlGenerator.describeTable(schemaName = tableName.namespace, tableName = tableName.name)
        dataSource.connection.use { connection ->
            val rs: ResultSet = connection.createStatement().executeQuery(sql)
            val columnsInDb: MutableSet<ColumnDefinition> = mutableSetOf()

            while (rs.next()) {
                val columnName = rs.getString("name")
                // Filter out airbyte columns
                if (COLUMN_NAMES.contains(columnName)) {
                    continue
                }
                val dataType = rs.getString("type").takeWhile { char -> char != '(' }

                val isNullable = rs.getString("null?") == "Y"
                columnsInDb.add(ColumnDefinition(columnName, dataType, isNullable))
            }

            val columnsInStream: Set<ColumnDefinition> =
                stream.schema
                    .asColumns()
                    .map { (name, fieldType) ->
                        // Snowflake is case-insensitive by default and stores identifiers in
                        // uppercase.
                        // We should probably be using the mapping in columnNameMapping, but for
                        // now, this is a good enough approximation.
                        val mappedName = columnNameMapping.get(name) ?: name
                        ColumnDefinition(
                            mappedName,
                            snowflakeColumnUtils.toDialectType(fieldType.type).takeWhile { char ->
                                char != '('
                            },
                            fieldType.nullable
                        )
                    }
                    .toSet()

            val addedColumns =
                columnsInStream.filter { it.name !in columnsInDb.map { it.name } }.toSet()
            val deletedColumns =
                columnsInDb.filter { it.name !in columnsInStream.map { it.name } }.toSet()
            val commonColumns =
                columnsInStream.filter { it.name in columnsInDb.map { it.name } }.toSet()
            val modifiedColumns =
                commonColumns
                    .filter {
                        val dbType = columnsInDb.find { column -> it.name == column.name }?.type
                        it.type != dbType
                    }
                    .toSet()

            if (
                addedColumns.isNotEmpty() ||
                    deletedColumns.isNotEmpty() ||
                    modifiedColumns.isNotEmpty()
            ) {
                log.error { "Summary of the table alterations:" }
                log.error { "Added columns: $addedColumns" }
                log.error { "Deleted columns: $deletedColumns" }
                log.error { "Modified columns: $modifiedColumns" }
                log.error {
                    sqlGenerator.alterTable(
                        tableName,
                        addedColumns,
                        deletedColumns,
                        modifiedColumns
                    )
                }
                sqlGenerator
                    .alterTable(tableName, addedColumns, deletedColumns, modifiedColumns)
                    .forEach { execute(it) }
            }
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            val sql = sqlGenerator.getGenerationId(tableName)
            dataSource.connection.use { connection ->
                val resultSet = connection.createStatement().executeQuery(sql)
                if (resultSet.next()) {
                    resultSet.getLong(COLUMN_NAME_AB_GENERATION_ID)
                } else {
                    log.warn { "No generation ID found for table $tableName, returning 0" }
                    0L
                }
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve the generation ID for table $tableName" }
            // Return 0 if we can't get the generation ID (similar to ClickHouse approach)
            0L
        }

    suspend fun createSnowflakeStage(tableName: TableName) {
        execute(sqlGenerator.createSnowflakeStage(tableName))
    }

    suspend fun putInStage(tableName: TableName, tempFilePath: String) {
        execute(sqlGenerator.putInStage(tableName, tempFilePath))
    }

    suspend fun copyFromStage(tableName: TableName) {
        execute(sqlGenerator.copyFromStage(tableName))
    }

    fun describeTable(tableName: TableName): List<String> =
        dataSource.connection.use { connection ->
            val resultSet =
                connection.createStatement().executeQuery(sqlGenerator.showColumns(tableName))
            val columns = mutableListOf<String>()
            while (resultSet.next()) {
                columns.add(resultSet.getString(DESCRIBE_TABLE_COLUMN_NAME_FIELD))
            }
            return columns
        }

    internal fun execute(query: String) =
        dataSource.connection.use { connection -> connection.createStatement().executeQuery(query) }
}
