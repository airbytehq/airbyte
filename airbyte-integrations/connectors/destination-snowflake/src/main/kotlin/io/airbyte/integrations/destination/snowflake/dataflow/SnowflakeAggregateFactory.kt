/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import jakarta.inject.Singleton

@Singleton
class SnowflakeAggregateFactory(
    private val snowflakeClient: SnowflakeAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val columns = snowflakeClient.describeTable(tableName)

        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = columns,
                snowflakeClient = snowflakeClient
            )

        return SnowflakeAggregate(buffer = buffer)
    }
}
