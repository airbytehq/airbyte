/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.write.load.PostgresInsertBuffer
import jakarta.inject.Singleton

@Singleton
class PostgresAggregateFactory(
    private val postgresClient: PostgresAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val postgresConfiguration: PostgresConfiguration,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val buffer =
            PostgresInsertBuffer(
                tableName = tableName,
                columns = postgresClient.describeTable(tableName),
                postgresClient = postgresClient,
                postgresConfiguration = postgresConfiguration
            )
        return PostgresAggregate(buffer = buffer)
    }
}
