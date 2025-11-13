/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.mysql_v2.write.load.MysqlInsertBuffer

/**
 * MySQL implementation of Aggregate.
 * Delegates record accumulation and flushing to MysqlInsertBuffer.
 */
class MysqlAggregate(
    private val buffer: MysqlInsertBuffer,
) : Aggregate {
    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}
