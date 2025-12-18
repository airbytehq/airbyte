/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeRecordFormatter
import jakarta.inject.Singleton

@Singleton
class SnowflakeAggregateFactory(
    private val snowflakeClient: SnowflakeAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val catalog: DestinationCatalog,
    private val columnManager: SnowflakeColumnManager,
    private val snowflakeRecordFormatter: SnowflakeRecordFormatter,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val stream = catalog.getStream(key)
        val tableName = streamStateStore.get(key)!!.tableName

        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeClient,
                snowflakeConfiguration = snowflakeConfiguration,
                columnSchema = stream.tableSchema.columnSchema,
                columnManager = columnManager,
                snowflakeRecordFormatter = snowflakeRecordFormatter,
            )
        return SnowflakeAggregate(buffer = buffer)
    }
}
