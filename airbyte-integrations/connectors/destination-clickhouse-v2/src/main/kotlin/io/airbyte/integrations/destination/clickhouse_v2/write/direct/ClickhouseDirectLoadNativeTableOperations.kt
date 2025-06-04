package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.BaseDirectLoadTableNativeOperations
import io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseAirbyteClient
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoadNativeTableOperations(
    client: ClickhouseAirbyteClient
):
    BaseDirectLoadTableNativeOperations<ClickHouseDataType>(client) {
    // TODO: implement this.
    override fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        // No alteration for now
    }
}
