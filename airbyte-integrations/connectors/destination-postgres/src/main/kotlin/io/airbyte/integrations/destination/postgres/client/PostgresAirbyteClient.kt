/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.client

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.postgres.sql.PostgresDirectLoadSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

internal const val COUNT_TOTAL_ALIAS = "total"

@Singleton
class PostgresAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: PostgresDirectLoadSqlGenerator,
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
        replace: Boolean
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
    ) = TODO("PostgresAirbyteClient.ensureSchemaMatches not yet implemented")

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

    internal fun execute(query: String) =
        dataSource.connection.use { connection -> connection.createStatement().executeQuery(query) }
}
