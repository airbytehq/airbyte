/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateEntry
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.airbyte.cdk.load.dataflow.state.stats.CommittedStatsStore
import io.mockk.Runs
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class PipelineCompletionHandlerTest {

    @MockK private lateinit var aggStore: AggregateStore

    @MockK private lateinit var stateHistogramStore: StateHistogramStore

    @MockK private lateinit var statsStore: CommittedStatsStore

    private lateinit var pipelineCompletionHandler: PipelineCompletionHandler

    @BeforeEach
    fun setUp() {
        pipelineCompletionHandler =
            PipelineCompletionHandler(
                aggStore = aggStore,
                stateHistogramStore = stateHistogramStore,
                statsStore = statsStore,
            )
    }

    @Test
    fun `apply should throw exception when cause is provided`() = runTest {
        // Given
        val testException = RuntimeException("Test exception")

        // When & Then
        val thrownException =
            assertThrows<RuntimeException> { pipelineCompletionHandler.apply(testException) }

        assertEquals("Test exception", thrownException.message)
    }

    @Test
    fun `apply flushes remaining aggregates and states if no cause is provided`() = runTest {
        // Given
        val mockAggregate1 = mockk<Aggregate>()
        val mockAggregate2 = mockk<Aggregate>()
        val mockCountsHistogram1 = mockk<PartitionHistogram>()
        val mockCountsHistogram2 = mockk<PartitionHistogram>()
        val mockBytesHistogram1 = mockk<PartitionHistogram>()
        val mockBytesHistogram2 = mockk<PartitionHistogram>()

        val aggregateEntry1 =
            AggregateEntry(
                key = Fixtures.key,
                value = mockAggregate1,
                partitionCountsHistogram = mockCountsHistogram1,
                partitionBytesHistogram = mockBytesHistogram1,
                stalenessTrigger = mockk(),
                recordCountTrigger = mockk(),
                estimatedBytesTrigger = mockk()
            )

        val aggregateEntry2 =
            AggregateEntry(
                key = Fixtures.key,
                value = mockAggregate2,
                partitionCountsHistogram = mockCountsHistogram2,
                partitionBytesHistogram = mockBytesHistogram2,
                stalenessTrigger = mockk(),
                recordCountTrigger = mockk(),
                estimatedBytesTrigger = mockk()
            )

        every { aggStore.getAll() } returns listOf(aggregateEntry1, aggregateEntry2)
        coEvery { mockAggregate1.flush() } just Runs
        coEvery { mockAggregate2.flush() } just Runs
        every { stateHistogramStore.acceptFlushedCounts(any()) } returns mockk()
        every { statsStore.acceptStats(any(), any(), any()) } returns mockk()

        // When
        pipelineCompletionHandler.apply(null)

        // Then
        coVerify(exactly = 1) { mockAggregate1.flush() }
        coVerify(exactly = 1) { mockAggregate2.flush() }
        verify(exactly = 1) { stateHistogramStore.acceptFlushedCounts(mockCountsHistogram1) }
        verify(exactly = 1) { stateHistogramStore.acceptFlushedCounts(mockCountsHistogram2) }
        verify(exactly = 1) {
            statsStore.acceptStats(Fixtures.key, mockCountsHistogram1, mockBytesHistogram1)
        }
        verify(exactly = 1) {
            statsStore.acceptStats(Fixtures.key, mockCountsHistogram2, mockBytesHistogram2)
        }
    }

    @Test
    fun `apply should handle empty aggregates list`() = runTest {
        // Given
        every { aggStore.getAll() } returns emptyList()

        // When
        pipelineCompletionHandler.apply(null)

        // Then
        verify(exactly = 1) { aggStore.getAll() }
        verify(exactly = 0) { stateHistogramStore.acceptFlushedCounts(any()) }
        verify(exactly = 0) { statsStore.acceptStats(any(), any(), any()) }
    }

    @Test
    fun `apply should handle aggregate flush failure`() = runTest {
        // Given
        val mockAggregate = mockk<Aggregate>()
        val mockCountsHistogram = mockk<PartitionHistogram>()
        val mockBytesHistogram = mockk<PartitionHistogram>()
        val flushException = RuntimeException("Flush failed")

        val aggregateEntry =
            AggregateEntry(
                key = Fixtures.key,
                value = mockAggregate,
                partitionCountsHistogram = mockCountsHistogram,
                partitionBytesHistogram = mockBytesHistogram,
                stalenessTrigger = mockk(),
                recordCountTrigger = mockk(),
                estimatedBytesTrigger = mockk()
            )

        every { aggStore.getAll() } returns listOf(aggregateEntry)
        coEvery { mockAggregate.flush() } throws flushException

        // When & Then
        assertThrows<RuntimeException> { pipelineCompletionHandler.apply(null) }

        coVerify(exactly = 1) { mockAggregate.flush() }
        // Note: acceptFlushedCounts should not be called if flush fails
        verify(exactly = 0) { stateHistogramStore.acceptFlushedCounts(any()) }
        verify(exactly = 0) { statsStore.acceptStats(any(), any(), any()) }
    }

    object Fixtures {
        val key = StoreKey("namespace", "name")
    }
}
