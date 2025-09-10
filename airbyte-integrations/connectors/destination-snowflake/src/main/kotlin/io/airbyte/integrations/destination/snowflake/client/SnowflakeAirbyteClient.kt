/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import net.snowflake.ingest.streaming.InsertValidationResponse
import net.snowflake.ingest.streaming.OpenChannelRequest
import net.snowflake.ingest.streaming.SnowflakeStreamingIngestChannel
import net.snowflake.ingest.streaming.SnowflakeStreamingIngestClient
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class SnowflakeAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val snowflakeIngestClient: SnowflakeStreamingIngestClient,
    private val config: SnowflakeConfiguration,
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

    suspend fun insertRecordsUsingIngestClient(
        tableName: TableName,
        records: List<Map<String, AirbyteValue>>
    ): InsertValidationResponse {
        log.info { "Inserting ${records.size} records into ${tableName.name} using ingest client" }
        
        val openChannelRequest = OpenChannelRequest.builder("AIRBYTE_CHANNEL_${tableName.namespace}_${tableName.name}")
            .setDBName(config.database)
            .setSchemaName(tableName.namespace)
            .setTableName(tableName.name)
            .build()
        
        val channel: SnowflakeStreamingIngestChannel = snowflakeIngestClient.openChannel(openChannelRequest)
        
        val rows = records.map { record ->
            record.mapValues { (_, value) ->
                when (value) {
                    is StringValue -> value.value
                    is IntegerValue -> value.value.toString()
                    is NumberValue -> value.value.toString()
                    is BooleanValue -> value.value
                    is DateValue -> value.value.toString()
                    is TimestampWithTimezoneValue -> value.value.toString()
                    is TimestampWithoutTimezoneValue -> value.value.toString()
                    is TimeWithTimezoneValue -> value.value.toString()
                    is TimeWithoutTimezoneValue -> value.value.toString()
                    is ArrayValue -> value.values.toString()
                    is ObjectValue -> value.values
                    is NullValue -> null
                }
            }
        }
        
        val response = channel.insertRows(rows, null)
        
        if (response.hasErrors()) {
            log.error { "Insert errors occurred: ${response.insertErrors}" }
        } else {
            log.info { "Successfully inserted ${records.size} records into ${tableName.name}" }
        }
        
        return response
    }

    internal fun execute(query: String): ResultSet {
        return dataSource.connection.use { connection ->
            connection.createStatement().executeQuery(query)
        }
    }
}
