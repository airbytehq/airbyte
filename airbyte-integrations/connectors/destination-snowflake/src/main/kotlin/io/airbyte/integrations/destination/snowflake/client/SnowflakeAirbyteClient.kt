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
import jakarta.inject.Singleton

@Singleton
class AirbyteSnowflakeClient(
    private val dataSource: HikariDataSource,
    private val sqlGenerator: SnowflakeSqlGenerator,
) : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {
    override suspend fun countTable(tableName: TableName): Long? {
        TODO("Not yet implemented")
    }

    override suspend fun createNamespace(namespace: String) {
        TODO("Not yet implemented")
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        TODO("Not yet implemented")
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        TODO("Not yet implemented")
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        TODO("Not yet implemented")
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        TODO("Not yet implemented")
    }

    override suspend fun dropTable(tableName: TableName) {
        TODO("Not yet implemented")
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        TODO("Not yet implemented")
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        TODO("Not yet implemented")
    }
}
