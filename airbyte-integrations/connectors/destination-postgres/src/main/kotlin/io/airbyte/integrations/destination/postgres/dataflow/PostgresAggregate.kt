/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.postgres.write.load.PostgresInsertBuffer
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

class PostgresAggregate(
    private val buffer: PostgresInsertBuffer,
) : Aggregate {
    override fun accept(record: RecordDTO) {
        log.info { "received a record" }
        buffer.accumulate(record.fields)
    }

    override suspend fun flush() {
        buffer.flush()
    }
}
