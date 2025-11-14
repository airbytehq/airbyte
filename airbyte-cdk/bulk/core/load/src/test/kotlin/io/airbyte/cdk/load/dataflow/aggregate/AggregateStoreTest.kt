/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.mockk.Runs
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlin.time.Duration.Companion.seconds
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class AggregateStoreTest {

    @MockK private lateinit var aggregateFactory: AggregateFactory
    @MockK private lateinit var mockAggregate: Aggregate
    private lateinit var memoryConfig: AggregatePublishingConfig
    private lateinit var aggregateStore: AggregateStore

    private val testKey = DestinationStream.Descriptor(namespace = "test", name = "stream")

    @BeforeEach
    fun setUp() {
        every { mockAggregate.accept(any()) } just Runs
        every { aggregateFactory.create(any()) } returns mockAggregate

        memoryConfig =
            AggregatePublishingConfig(
                maxEstBytesAllAggregates = 5000L,
                maxRecordsPerAgg = 100L,
                maxEstBytesPerAgg = 2000L,
                stalenessDeadlinePerAgg = 10.seconds
            )

        aggregateStore = AggregateStore(aggregateFactory, memoryConfig)
    }

    @Test
    fun `acceptFor should create new aggregate entry if not exists`() {
        val record = Fixtures.dto(partitionKey = "partition1", sizeBytes = 50, emittedAtMs = 1000L)

        assertEquals(0, aggregateStore.getAll().size)
        aggregateStore.acceptFor(testKey, record)

        assertEquals(1, aggregateStore.getAll().size)

        verify { aggregateFactory.create(testKey) }
        verify { mockAggregate.accept(record) }
    }

    @Test
    fun `acceptFor should reuse existing aggregate entry`() {
        val record1 = Fixtures.dto(partitionKey = "partition1", sizeBytes = 50, emittedAtMs = 1000L)
        val record2 = Fixtures.dto(partitionKey = "partition2", sizeBytes = 30, emittedAtMs = 2000L)

        aggregateStore.acceptFor(testKey, record1)
        aggregateStore.acceptFor(testKey, record2)

        verify(exactly = 1) { aggregateFactory.create(testKey) }
        verify { mockAggregate.accept(record1) }
        verify { mockAggregate.accept(record2) }

        val entries = aggregateStore.getAll()
        assertEquals(1, entries.size)
    }

    @Test
    fun `acceptFor makes new entries per key`() {
        val newKey = DestinationStream.Descriptor(namespace = "test", name = "other-stream")
        val newAggregate = mockk<Aggregate>(relaxed = true)
        every { aggregateFactory.create(testKey) } returns mockAggregate
        every { aggregateFactory.create(newKey) } returns newAggregate

        val record1 = Fixtures.dto(partitionKey = "partition1", sizeBytes = 50, emittedAtMs = 1000L)
        val record2 = Fixtures.dto(partitionKey = "partition2", sizeBytes = 30, emittedAtMs = 2000L)

        aggregateStore.acceptFor(testKey, record1)
        aggregateStore.acceptFor(newKey, record2)

        verify(exactly = 1) { aggregateFactory.create(testKey) }
        verify(exactly = 1) { aggregateFactory.create(newKey) }
        verify { mockAggregate.accept(record1) }
        verify { newAggregate.accept(record2) }

        val entries = aggregateStore.getAll()
        assertEquals(2, entries.size)
        assertTrue(entries.any { it.key == testKey })
        assertTrue(entries.any { it.key == newKey })
    }

    @Test
    fun `acceptFor should update triggers correctly`() {
        val record = Fixtures.dto(partitionKey = "partition1", sizeBytes = 50, emittedAtMs = 1000L)

        aggregateStore.acceptFor(testKey, record)

        val entry = aggregateStore.getOrCreate(testKey)
        assertEquals(1L, entry.recordCountTrigger.watermark())
        assertEquals(50L, entry.estimatedBytesTrigger.watermark())
        assertEquals(1L, entry.partitionCountsHistogram.get(PartitionKey("partition1"))?.toLong())
        assertEquals(50L, entry.partitionBytesHistogram.get(PartitionKey("partition1"))?.toLong())
    }

    @Test
    fun `removeNextComplete should remove complete aggregate by record count`() {
        // Add records to reach the record count limit
        repeat(100) { i ->
            val record =
                Fixtures.dto(partitionKey = "partition1", sizeBytes = 5, emittedAtMs = 1000L + i)
            aggregateStore.acceptFor(testKey, record)
        }

        val result = aggregateStore.removeNextComplete(2000L)

        assertNotNull(result)
        assertTrue(result.isComplete())
        assertEquals(0, aggregateStore.getAll().size)
    }

    @Test
    fun `removeNextComplete should remove complete aggregate by bytes`() {
        // Add records to reach the bytes limit
        repeat(20) {
            val record =
                Fixtures.dto(partitionKey = "partition1", sizeBytes = 110, emittedAtMs = 2000L)
            aggregateStore.acceptFor(testKey, record)
        }

        val result = aggregateStore.removeNextComplete(2000L)

        assertNotNull(result)
        assertTrue(result.isComplete())
        assertEquals(0, aggregateStore.getAll().size)
    }

    @Test
    fun `removeNextComplete should remove stale aggregate`() {
        val record = Fixtures.dto(partitionKey = "partition1", sizeBytes = 10, emittedAtMs = 1000L)
        aggregateStore.acceptFor(testKey, record)

        // Check after staleness deadline (10 seconds = 10000ms)
        val result = aggregateStore.removeNextComplete(11001L)

        assertNotNull(result)
        assertTrue(result.isStale(11001L))
        assertEquals(0, aggregateStore.getAll().size)
    }

    @Test
    fun `removeNextComplete should evict largest aggregate when exceeding max total bytes`() {
        val iterations = 5
        val keys =
            (1..iterations).map { i ->
                DestinationStream.Descriptor(namespace = "test", name = "stream$i")
            }

        keys.forEachIndexed { index, key ->
            // make the 2nd aggregate bigger than the others so we exceed maxEstBytesAllAggregates
            val recordSize =
                if (key.name == "stream2") {
                    (memoryConfig.maxEstBytesAllAggregates / iterations) * 2
                } else {
                    memoryConfig.maxEstBytesAllAggregates / iterations
                }

            val record =
                Fixtures.dto(
                    partitionKey = "partition$index",
                    sizeBytes = recordSize,
                    emittedAtMs = 1000L
                )
            aggregateStore.acceptFor(key, record)
        }

        // we have an aggregate per key
        assertEquals(keys.size, aggregateStore.getAll().size)

        // Now we have 6000 bytes of aggregates, but max is 5000
        val result = aggregateStore.removeNextComplete(1000L)

        // we return an aggregates
        assertNotNull(result)
        // It should be the largest one
        assertEquals("stream2", result.key.name)
        // total aggregates less than before
        assertEquals(keys.size - 1, aggregateStore.getAll().size)
    }

    @Test
    fun `getAll should return all current aggregates`() {
        val keys =
            listOf(
                DestinationStream.Descriptor(namespace = "test", name = "stream1"),
                DestinationStream.Descriptor(namespace = "test", name = "stream2"),
                DestinationStream.Descriptor(namespace = "test", name = "stream3")
            )

        keys.forEach { key ->
            val record =
                Fixtures.dto(partitionKey = "partition", sizeBytes = 10, emittedAtMs = 1000L)
            aggregateStore.acceptFor(key, record)
        }

        val entries = aggregateStore.getAll()
        assertEquals(3, entries.size)
    }

    @Test
    fun `AggregateEntry isComplete should return true when record count trigger is complete`() {
        val entry =
            AggregateEntry(
                key = Fixtures.key,
                value = mockAggregate,
                partitionCountsHistogram = PartitionHistogram(),
                partitionBytesHistogram = PartitionHistogram(),
                stalenessTrigger = TimeTrigger(10000),
                recordCountTrigger = SizeTrigger(10).apply { repeat(10) { increment(1) } },
                estimatedBytesTrigger = SizeTrigger(1000)
            )

        assertTrue(entry.isComplete())
    }

    @Test
    fun `AggregateEntry isComplete should return true when bytes trigger is complete`() {
        val entry =
            AggregateEntry(
                key = Fixtures.key,
                value = mockAggregate,
                partitionCountsHistogram = PartitionHistogram(),
                partitionBytesHistogram = PartitionHistogram(),
                stalenessTrigger = TimeTrigger(10000),
                recordCountTrigger = SizeTrigger(100),
                estimatedBytesTrigger = SizeTrigger(1000).apply { increment(1000) }
            )

        assertTrue(entry.isComplete())
    }

    @Test
    fun `AggregateEntry isComplete should return false when neither trigger is complete`() {
        val entry =
            AggregateEntry(
                key = Fixtures.key,
                value = mockAggregate,
                partitionCountsHistogram = PartitionHistogram(),
                partitionBytesHistogram = PartitionHistogram(),
                stalenessTrigger = TimeTrigger(10000),
                recordCountTrigger = SizeTrigger(100),
                estimatedBytesTrigger = SizeTrigger(1000)
            )

        assertFalse(entry.isComplete())
    }

    @Test
    fun `AggregateEntry isStale should delegate to time trigger`() {
        val entry =
            AggregateEntry(
                key = Fixtures.key,
                value = mockAggregate,
                partitionCountsHistogram = PartitionHistogram(),
                partitionBytesHistogram = PartitionHistogram(),
                stalenessTrigger = TimeTrigger(1000).apply { update(5000) },
                recordCountTrigger = SizeTrigger(100),
                estimatedBytesTrigger = SizeTrigger(1000)
            )

        assertFalse(entry.isStale(5500))
        assertTrue(entry.isStale(6000))
    }

    @Test
    fun `concurrent access should be thread safe`() {
        val threads =
            (1..10).map { threadId ->
                Thread {
                    repeat(10) { recordId ->
                        val key =
                            DestinationStream.Descriptor(
                                namespace = "test",
                                name = "stream$threadId"
                            )
                        val record =
                            Fixtures.dto(
                                partitionKey = "partition$recordId",
                                sizeBytes = 10,
                                emittedAtMs = System.currentTimeMillis()
                            )
                        aggregateStore.acceptFor(key, record)
                    }
                }
            }

        threads.forEach { it.start() }
        threads.forEach { it.join() }

        val entries = aggregateStore.getAll()
        assertTrue(entries.size == 10)
    }

    object Fixtures {
        val key = StoreKey("namespace", "name")

        fun dto(partitionKey: String, sizeBytes: Long, emittedAtMs: Long): RecordDTO =
            RecordDTO(
                fields = mapOf(),
                partitionKey = PartitionKey(partitionKey),
                sizeBytes = sizeBytes,
                emittedAtMs = emittedAtMs,
            )
    }
}
