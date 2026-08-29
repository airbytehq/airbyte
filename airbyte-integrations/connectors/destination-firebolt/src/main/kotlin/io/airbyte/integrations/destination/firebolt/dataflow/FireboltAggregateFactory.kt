/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.firebolt.client.FireboltAirbyteClient
import io.airbyte.integrations.destination.firebolt.config.FireboltConfiguration
import io.airbyte.integrations.destination.firebolt.write.load.FireboltInsertBuffer
import jakarta.inject.Singleton

/** Factory for creating [FireboltAggregate] instances, one per stream. */
@Singleton
class FireboltAggregateFactory(
    private val fireboltClient: FireboltAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val configuration: FireboltConfiguration,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val columns = fireboltClient.describeTable(tableName)
        val buffer =
            FireboltInsertBuffer(
                tableName = tableName,
                columns = columns,
                fireboltClient = fireboltClient,
                configuration = configuration,
            )
        return FireboltAggregate(buffer = buffer)
    }
}
