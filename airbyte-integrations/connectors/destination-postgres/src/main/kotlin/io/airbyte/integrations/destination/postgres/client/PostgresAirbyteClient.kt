/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.client

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import jakarta.inject.Singleton

@Singleton
class PostgresAirbyteClient : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {

    override suspend fun countTable(tableName: TableName): Long? {
        throw NotImplementedError("PostgresAirbyteClient.countTable not yet implemented")
    }

    override suspend fun createNamespace(namespace: String) {
        throw NotImplementedError("PostgresAirbyteClient.createNamespace not yet implemented")
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        throw NotImplementedError("PostgresAirbyteClient.createTable not yet implemented")
    }

    override suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        throw NotImplementedError("PostgresAirbyteClient.overwriteTable not yet implemented")
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        throw NotImplementedError("PostgresAirbyteClient.copyTable not yet implemented")
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        throw NotImplementedError("PostgresAirbyteClient.upsertTable not yet implemented")
    }

    override suspend fun dropTable(tableName: TableName) {
        throw NotImplementedError("PostgresAirbyteClient.dropTable not yet implemented")
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        throw NotImplementedError("PostgresAirbyteClient.ensureSchemaMatches not yet implemented")
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        throw NotImplementedError("PostgresAirbyteClient.getGenerationId not yet implemented")
    }
}
