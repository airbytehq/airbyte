/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.write.load.RedshiftInsertBuffer
import jakarta.inject.Singleton

/** Factory for creating [RedshiftAggregate] instances, one per stream */
@Singleton
class RedshiftAggregateFactory(
    private val redshiftClient: RedshiftAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val redshiftConfiguration: RedshiftConfiguration,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val columns = redshiftClient.describeTable(tableName)
        val buffer =
            RedshiftInsertBuffer(
                tableName = tableName,
                columns = columns,
                redshiftClient = redshiftClient,
                configuration = redshiftConfiguration,
            )
        return RedshiftAggregate(buffer = buffer)
    }
}
