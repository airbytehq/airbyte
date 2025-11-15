/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.dataflow

import com.google.common.annotations.VisibleForTesting
import com.mongodb.kotlin.client.coroutine.MongoClient
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mongodb_v2.config.MongodbConfiguration
import io.airbyte.integrations.destination.mongodb_v2.write.load.MongodbInsertBuffer
import io.micronaut.context.annotation.Factory

class MongodbAggregate(
    @VisibleForTesting val buffer: MongodbInsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}

@Factory
class MongodbAggregateFactory(
    private val mongoClient: MongoClient,
    private val config: MongodbConfiguration,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName

        val insertBuffer =
            MongodbInsertBuffer(
                tableName,
                mongoClient,
                tableName.namespace ?: config.resolvedDatabase,
            )

        return MongodbAggregate(insertBuffer)
    }
}
