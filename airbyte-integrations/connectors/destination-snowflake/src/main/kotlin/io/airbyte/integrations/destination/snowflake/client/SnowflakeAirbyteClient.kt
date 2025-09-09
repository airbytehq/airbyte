/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet

val log = KotlinLogging.logger {}

@Singleton
class SnowflakeAirbyteClient(
    private val dataSource: HikariDataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
) : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {
    override suspend fun countTable(tableName: TableName): Long {
        return execute(sqlGenerator.countTable(tableName)).getInt("total").toLong()
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
            val sql = sqlGenerator.getGenerationId(tableName, "generation")
            val resultSet = execute(sql)
            if (resultSet.next()) {
                resultSet.getLong("generation")
            } else {
                log.warn { "No generation ID found for table $tableName, returning 0" }
                0L
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve the generation ID for table $tableName" }
            // Return 0 if we can't get the generation ID (similar to ClickHouse approach)
            0L
        }
    }

    internal fun execute(query: String): ResultSet {
        return dataSource.connection.use { connection ->
            connection.createStatement().executeQuery(query)
        }
    }
}
