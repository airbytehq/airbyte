/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.snowflake.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import javax.sql.DataSource

internal const val DESCRIBE_TABLE_COLUMN_NAME_FIELD = "column_name"
internal const val GENERATION_ID_ALIAS = "generation"

private val log = KotlinLogging.logger {}

@Singleton
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
) : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {
    override suspend fun countTable(tableName: TableName): Long {
        return dataSource.connection.use { connection ->
            val resultSet =
                connection.createStatement().executeQuery(sqlGenerator.countTable(tableName))

            if (resultSet.next()) {
                resultSet.getLong(COUNT_TOTAL_ALIAS)
            } else {
                0L
            }
        }
    }

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
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
        TODO("Not yet implemented")
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
        TODO("Not yet implemented")
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        return try {
            val sql = sqlGenerator.getGenerationId(tableName, GENERATION_ID_ALIAS)
            dataSource.connection.use { connection ->
                val resultSet = connection.createStatement().executeQuery(sql)
                if (resultSet.next()) {
                    resultSet.getLong(GENERATION_ID_ALIAS)
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
    }

    suspend fun createFileFormat() {
        execute(sqlGenerator.createFileFormat())
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

    internal fun execute(query: String) {
        return dataSource.connection.use { connection ->
            connection.createStatement().executeQuery(query)
        }
    }
}
