/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.databricksv2.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricksv2.spec.DatabricksV2Configuration
import io.airbyte.integrations.destination.databricksv2.write.load.DatabricksInsertBuffer
import jakarta.inject.Singleton

@Singleton
class DatabricksAggregateFactory(
    private val databricksClient: DatabricksAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val config: DatabricksV2Configuration,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val columnSchema = databricksClient.describeTable(tableName)
        val buffer =
            DatabricksInsertBuffer(
                tableName = tableName,
                columns = columnSchema.keys.toList(),
                columnSchema = columnSchema,
                databricksClient = databricksClient,
                config = config,
            )
        return DatabricksAggregate(buffer = buffer)
    }
}
