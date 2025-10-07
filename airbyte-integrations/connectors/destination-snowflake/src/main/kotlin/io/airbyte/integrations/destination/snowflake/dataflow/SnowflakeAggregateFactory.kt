/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

@Singleton
class SnowflakeAggregateFactory(
    private val snowflakeClient: SnowflakeAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
) : AggregateFactory {
    // We assume that a table isn't getting altered _during_ a sync.
    // This allows us to only SHOW COLUMNS once per table per sync,
    // rather than refetching it on every aggregate.
    private val columnsByKey: ConcurrentMap<TableName, List<String>> = ConcurrentHashMap()

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = getTableColumns(tableName),
                snowflakeClient = snowflakeClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )
        return SnowflakeAggregate(buffer = buffer)
    }

    private fun getTableColumns(tableName: TableName) =
        columnsByKey.getOrPut(tableName) { snowflakeClient.describeTable(tableName) }
}
