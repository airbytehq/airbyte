/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class DevNullAggregateTest {
    private val stream = DestinationStream.Descriptor("ns", "users")
    private val record =
        RecordDTO(fields = emptyMap(), partitionKey = PartitionKey("p"), sizeBytes = 1L, emittedAtMs = 0L)

    @Test
    fun `logging counters continue across aggregates of the same stream`() {
        val factory = DevNullAggregateFactory(DevNullConfiguration(Logging(maxEntryCount = 3)))

        repeat(2) { factory.create(stream).accept(record) }
        val second = factory.create(stream)
        repeat(5) { second.accept(record) }

        val counters = factory.countersFor(stream)
        assertEquals(7L, counters.recordCount.get())
        assertEquals(7L, counters.logCount.get(), "every record is a log candidate when N=1")
    }

    @Test
    fun `every nth entry uses the stream-wide record index`() {
        val counters = StreamCounters()
        val aggregate =
            LoggingAggregate(logEveryN = 3, streamDescriptor = stream, counters = counters)
        repeat(9) { aggregate.accept(record) }
        assertEquals(3L, counters.logCount.get())
    }

    @Test
    fun `seeded sampling is deterministic`() {
        fun run(): Long {
            val counters = StreamCounters()
            val aggregate =
                LoggingAggregate(
                    logEveryN = 1,
                    streamDescriptor = stream,
                    sampleRate = 0.5,
                    seed = 42L,
                    counters = counters,
                )
            repeat(100) { aggregate.accept(record) }
            return counters.logCount.get()
        }
        assertEquals(run(), run())
    }

    @Test
    fun `failing aggregate fails on the nth record across aggregates`() {
        val factory = DevNullAggregateFactory(DevNullConfiguration(Failing(numMessages = 5)))
        repeat(2) { factory.create(stream).accept(record) }
        val third = factory.create(stream)
        third.accept(record)
        third.accept(record)
        assertThrows(RuntimeException::class.java) { third.accept(record) }
    }

    @Test
    fun `streams are counted independently`() {
        val other = DestinationStream.Descriptor("ns", "orders")
        val factory = DevNullAggregateFactory(DevNullConfiguration(Failing(numMessages = 2)))
        factory.create(stream).accept(record)
        factory.create(other).accept(record)
        assertThrows(RuntimeException::class.java) { factory.create(stream).accept(record) }
    }
}
