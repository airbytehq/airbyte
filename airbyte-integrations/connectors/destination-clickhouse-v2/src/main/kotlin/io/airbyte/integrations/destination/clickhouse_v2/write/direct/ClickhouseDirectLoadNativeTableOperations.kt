package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoadNativeTableOperations: DirectLoadTableNativeOperations {
    override fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        // No alteration for now
    }

    // TODO: this needs to be updated.
    override fun getGenerationId(tableName: TableName): Long = 0
}
