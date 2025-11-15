package io.airbyte.integrations.destination.mysql.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.mysql.write.load.MySQLInsertBuffer

class MySQLAggregate(
    private val buffer: MySQLInsertBuffer,
) : Aggregate {

    override fun accept(record: RecordDTO) {
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}
