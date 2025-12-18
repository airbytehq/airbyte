/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.table.directload.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.redshift_v2.write.load.RedshiftInsertBuffer
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import javax.sql.DataSource

/**
 * Processes transformed records for a single stream.
 * NOT a @Singleton - created per-stream by AggregateFactory.
 */
class RedshiftAggregate(
    private val buffer: RedshiftInsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}

@Factory
class RedshiftAggregateFactory(
    private val dataSource: DataSource,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {

    @Singleton
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName

        val buffer = RedshiftInsertBuffer(
            tableName = tableName,
            dataSource = dataSource,
        )

        return RedshiftAggregate(buffer)
    }
}
