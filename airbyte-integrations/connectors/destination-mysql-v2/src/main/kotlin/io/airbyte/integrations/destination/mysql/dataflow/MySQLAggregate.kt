/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.dataflow

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mysql.write.load.MySQLInsertBuffer
import io.micronaut.context.annotation.Factory
import javax.sql.DataSource

class MySQLAggregate(
    @VisibleForTesting val buffer: MySQLInsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}

@Factory
class MySQLAggregateFactory(
    private val dataSource: DataSource,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName

        val mysqlInsertBuffer = MySQLInsertBuffer(
            tableName,
            dataSource,
        )

        return MySQLAggregate(mysqlInsertBuffer)
    }
}
