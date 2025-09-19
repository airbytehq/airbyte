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
import io.airbyte.integrations.destination.snowflake.write.load.RawSnowflakeInsertBuffer
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import io.airbyte.integrations.destination.snowflake.write.load.StagingSnowflakeInsertBuffer
import jakarta.inject.Singleton

@Singleton
class SnowflakeAggregateFactory(
    private val snowflakeClient: SnowflakeAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val snowflakeConfiguration: SnowflakeConfiguration,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val buffer = createBuffer(tableName)
        return SnowflakeAggregate(buffer = buffer)
    }

    private fun createBuffer(tableName: TableName): SnowflakeInsertBuffer =
        if (snowflakeConfiguration.legacyRawTablesOnly == true) {
            RawSnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeClient,
            )
        } else {
            StagingSnowflakeInsertBuffer(
                tableName = tableName,
                columns = snowflakeClient.describeTable(tableName),
                snowflakeClient = snowflakeClient
            )
        }
}
