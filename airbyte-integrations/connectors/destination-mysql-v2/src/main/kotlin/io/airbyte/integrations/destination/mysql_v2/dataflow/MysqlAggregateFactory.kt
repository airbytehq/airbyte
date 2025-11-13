/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mysql_v2.client.MysqlAirbyteClient
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import io.airbyte.integrations.destination.mysql_v2.write.load.MysqlInsertBuffer
import jakarta.inject.Singleton

/**
 * Factory for creating MysqlAggregate instances.
 * Creates a MysqlInsertBuffer for each stream and wraps it in a MysqlAggregate.
 */
@Singleton
class MysqlAggregateFactory(
    private val mysqlClient: MysqlAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val config: MysqlConfiguration,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName

        // Get the column list for this table
        val columns = mysqlClient.describeTable(tableName)

        val buffer = MysqlInsertBuffer(
            tableName = tableName,
            columns = columns.keys.toList(),
            mysqlClient = mysqlClient,
            flushLimit = config.batchSize,
        )

        return MysqlAggregate(buffer = buffer)
    }
}
