/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.dataflow

import com.mongodb.client.MongoClient
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration
import io.airbyte.integrations.destination.mongodb_v2.write.MongodbInsertBuffer
import jakarta.inject.Singleton

@Singleton
class MongodbAggregateFactory(
    private val mongoClient: MongoClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val config: MongodbConfiguration,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val buffer =
            MongodbInsertBuffer(
                tableName = tableName,
                mongoClient = mongoClient,
                config = config,
            )
        return MongodbAggregate(buffer = buffer)
    }
}
