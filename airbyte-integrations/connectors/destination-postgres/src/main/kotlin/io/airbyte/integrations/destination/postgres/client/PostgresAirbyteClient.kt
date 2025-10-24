/*
* Copyright (c) 2025 Airbyte, Inc., all rights reserved.
*/

package io.airbyte.integrations.destination.postgres.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.sql.Column
import io.airbyte.integrations.destination.postgres.sql.PostgresDirectLoadSqlGenerator
import io.airbyte.integrations.destination.postgres.sql.PostgresDirectLoadSqlGenerator.Companion.COUNT_TOTAL_ALIAS
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import javax.sql.DataSource

private val log = KotlinLogging.logger {}


@Singleton
class PostgresAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: PostgresDirectLoadSqlGenerator,
) : TableSchemaEvolutionClient, TableOperationsClient {

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
        } catch (e: Exception) {
            log.debug(e) {
                "Table ${tableName.namespace}.${tableName.name} does not exist. Returning a null count to signal a missing table."
            }
            null
        }

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        execute(sqlGenerator.createTable(stream, tableName, columnNameMapping, replace))
    }

    override suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.overwriteTable(sourceTableName, targetTableName))
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
        execute(sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName))
    }

    override suspend fun dropTable(tableName: TableName) {
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

        if (
            addedColumns.isNotEmpty() || deletedColumns.isNotEmpty() || modifiedColumns.isNotEmpty()
        ) {
            log.info { "Summary of the table alterations:" }
            log.info { "Added columns: $addedColumns" }
            log.info { "Deleted columns: $deletedColumns" }
            log.info { "Modified columns: $modifiedColumns" }
            sqlGenerator
                .matchSchemas(tableName, addedColumns, deletedColumns, modifiedColumns)
                .forEach { execute(it) }
        }
    }

    internal fun getColumnsFromDb(tableName: TableName): Set<Column> {
        val sql =
            sqlGenerator.getTableSchema(tableName)
        dataSource.connection.use { connection ->
            val statement = connection.createStatement()
            return statement.use {
                val rs: ResultSet = it.executeQuery(sql)
                val columnsInDb: MutableSet<Column> = mutableSetOf()
                val defaultColumnNames = sqlGenerator.getDefaultColumnNames()
                while (rs.next()) {
                    //TODO: extract column_name and data_type as constants
                    val columnName = rs.getString("column_name")

                    // Filter out airbyte columns
                    if (defaultColumnNames.contains(columnName)) {
                        continue
                    }
                    val dataType = rs.getString("data_type")

                    columnsInDb.add(Column(columnName, dataType))
                }

                columnsInDb
            }
        }
    }

    internal fun getColumnsFromStream(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): Set<Column> {
        val defaultColumnNames = sqlGenerator.getDefaultColumnNames()
        return sqlGenerator.columnsAndTypes(stream, columnNameMapping)
            .filter { columnAndType -> columnAndType.columnName !in defaultColumnNames }
            .toSet()
    }

    internal fun generateSchemaChanges(
        columnsInDb: Set<Column>,
        columnsInStream: Set<Column>
    ): Triple<Set<Column>, Set<Column>, Set<Column>> {
        val addedColumns =
            columnsInStream.filter { it.columnName !in columnsInDb.map { col -> col.columnName } }.toSet()
        val deletedColumns =
            columnsInDb.filter { it.columnName !in columnsInStream.map { col -> col.columnName } }.toSet()
        val commonColumns =
            columnsInStream.filter { it.columnName in columnsInDb.map { col -> col.columnName } }.toSet()
        val modifiedColumns =
            commonColumns
                .filter {
                    val dbType = columnsInDb.find { column -> it.columnName == column.columnName }?.columnTypeName
                    it.columnTypeName != dbType
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
            0L
        }

    fun describeTable(tableName: TableName): List<String> =
        dataSource.connection.use { connection ->
            val resultSet =
                connection.createStatement().executeQuery(sqlGenerator.getTableSchema(tableName))
            val columns = mutableListOf<String>()
            while (resultSet.next()) {
                //TODO: extract column_name as a constant
                columns.add(resultSet.getString("column_name"))
            }
            return columns
        }

    fun copyFromCsv(tableName: TableName, filePath: String) {
        dataSource.connection.use { connection ->
            val copyManager = connection.unwrap(org.postgresql.core.BaseConnection::class.java)
                .getCopyAPI()
            val sql = sqlGenerator.copyFromCsv(tableName)
            java.io.FileInputStream(filePath).use { fileInputStream ->
                copyManager.copyIn(sql, fileInputStream)
            }
        }
    }

    private fun execute(query: String) =
        dataSource.connection.use { connection -> connection.createStatement().use { it.execute(query) }}
}
