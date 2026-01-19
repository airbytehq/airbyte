/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.schema.PostgresColumnManager
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.write.load.PostgresInsertBuffer
import jakarta.inject.Singleton

@Singleton
class PostgresAggregateFactory(
    private val postgresClient: PostgresAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val postgresConfiguration: PostgresConfiguration,
    private val catalog: DestinationCatalog,
    private val columnManager: PostgresColumnManager,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val stream = catalog.getStream(key)
        val tableName = streamStateStore.get(key)!!.tableName
        val buffer =
            PostgresInsertBuffer(
                tableName = tableName,
                postgresClient = postgresClient,
                postgresConfiguration = postgresConfiguration,
                columnSchema = stream.tableSchema.columnSchema,
                columnManager = columnManager,
            )
        return PostgresAggregate(buffer = buffer)
    }
}
