/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.command.CommandResponse
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.clickhouse.client.api.query.QueryResponse
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.future.await

val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
@Singleton
class ClickhouseAirbyteClient(
    private val client: ClickHouseClientRaw,
    private val sqlGenerator: ClickhouseSqlGenerator,
) : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {

    override suspend fun createNamespace(namespace: String) {
        val statement = sqlGenerator.createNamespace(namespace)

        execute(statement)
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        execute(
            sqlGenerator.createTable(
                stream,
                tableName,
                columnNameMapping,
                replace,
            ),
        )
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        execute(
            sqlGenerator.wrapInTransaction(
                sqlGenerator.dropTable(targetTableName),
                sqlGenerator.swapTable(sourceTableName, targetTableName),
            ),
        )
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(
            sqlGenerator.copyTable(
                columnNameMapping,
                sourceTableName,
                targetTableName,
            ),
        )
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(
            sqlGenerator.upsertTable(
                stream,
                columnNameMapping,
                sourceTableName,
                targetTableName,
            ),
        )
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        // TODO: ("Not yet implemented")
        // ensure transitioning from dedupe to non-dedupe and back works
    }

    override suspend fun countTable(tableName: TableName): Long? {
        try {
            val sql = sqlGenerator.countTable(tableName, "cnt")
            val response = query(sql)
            val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
            reader.next()
            val count = reader.getLong("cnt")
            return count
        } catch (e: Exception) {
            return null
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        try {
            val sql = sqlGenerator.getGenerationId(tableName, "generation")
            val response = query(sql)
            val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
            reader.next()
            val generation = reader.getLong("generation")
            return generation
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve the generation Id" }
            // TODO: open question: Do we need to raise an error here or just return 0?
            return 0
        }
    }

    private suspend fun execute(query: String): CommandResponse {
        return client.execute(query).await()
    }

    private suspend fun query(query: String): QueryResponse {
        return client.query(query).await()
    }
}
