/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.snowflake.db.ColumnDefinition
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.COUNT_TOTAL_ALIAS
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
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "kotlin coroutines")
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
    private val snowflakeConfiguration: SnowflakeConfiguration,
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
                "Table ${tableName.toPrettyString()} does not exist.  Returning a null count to signal a missing table."
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
        execute(sqlGenerator.dropStage(tableName))
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        val columnsInDb = getColumnsFromDb(tableName)
        val columnsInStream = getColumnsFromStream(stream, columnNameMapping)
        val (addedColumns, deletedColumns, modifiedColumns) =
            generateSchemaChanges(columnsInDb, columnsInStream)

        /*
         * If legacy raw tables are in use, there is nothing to ensure in schema, as raw mode
         * uses a fixed schema that is not based on the catalog/incoming record.  Otherwise,
         * ensure that the destination schema is in sync with any changes.
         */
        if (
            snowflakeConfiguration.legacyRawTablesOnly != true &&
                (addedColumns.isNotEmpty() ||
                    deletedColumns.isNotEmpty() ||
                    modifiedColumns.isNotEmpty())
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
            return columnsInDb
        }
    }

    internal fun getColumnsFromStream(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): Set<ColumnDefinition> {
        return stream.schema
            .asColumns()
            .map { (name, fieldType) ->
                // Snowflake is case-insensitive by default and stores identifiers in
                // uppercase.
                // We should probably be using the mapping in columnNameMapping, but for
                // now, this is a good enough approximation.
                val mappedName = columnNameMapping[name] ?: name
                ColumnDefinition(
                    mappedName,
                    snowflakeColumnUtils.toDialectType(fieldType.type).takeWhile { char ->
                        char != '('
                    },
                    fieldType.nullable
                )
            }
            .toSet()
    }

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

    fun createSnowflakeStage(tableName: TableName) {
        execute(sqlGenerator.createSnowflakeStage(tableName))
    }

    fun putInStage(tableName: TableName, tempFilePath: String) {
        execute(sqlGenerator.putInStage(tableName, tempFilePath))
    }

    fun copyFromStage(tableName: TableName) {
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
