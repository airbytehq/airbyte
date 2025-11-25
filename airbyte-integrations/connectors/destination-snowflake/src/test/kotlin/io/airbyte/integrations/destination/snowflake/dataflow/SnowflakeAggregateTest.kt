/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.dataflow

import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import io.mockk.coVerify
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test

internal class SnowflakeAggregateTest {

    @Test
    fun testAcceptingRecordsForAggregation() {
        val record = mockk<RecordDTO>(relaxed = true)
        val buffer = mockk<SnowflakeInsertBuffer>(relaxed = true)
        val aggregate = SnowflakeAggregate(buffer)
        aggregate.accept(record)
        verify(exactly = 1) { buffer.accumulate(any()) }
    }

    @Test
    fun testFlushingRecordsForAggregation() {
        val record = mockk<RecordDTO>(relaxed = true)
        val buffer = mockk<SnowflakeInsertBuffer>(relaxed = true)
        val aggregate = SnowflakeAggregate(buffer)
        aggregate.accept(record)
        runBlocking { aggregate.flush() }
        coVerify(exactly = 1) { buffer.flush() }
    }
}
