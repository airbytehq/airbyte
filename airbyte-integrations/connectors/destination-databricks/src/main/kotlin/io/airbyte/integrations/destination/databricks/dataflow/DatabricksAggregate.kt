/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.databricks.write.load.DatabricksInsertBuffer

class DatabricksAggregate(
    private val buffer: DatabricksInsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}
