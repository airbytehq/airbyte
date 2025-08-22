/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.dataflow

import com.clickhouse.client.api.Client
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse.write.load.BinaryRowInsertBuffer
import io.micronaut.context.annotation.Factory

class ClickhouseAggregate(
    @VisibleForTesting val buffer: BinaryRowInsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}

@Factory
class ClickhouseAggregateFactory(
    private val clickhouseClient: Client,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val tableName = TableName(name = key.name, namespace = key.namespace ?: "default")
        val binaryRowInsertBuffer =
            BinaryRowInsertBuffer(
                tableName,
                clickhouseClient,
            )

        return ClickhouseAggregate(binaryRowInsertBuffer)
    }
}
