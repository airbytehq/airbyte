/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateEntry
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.airbyte.cdk.load.dataflow.state.StateReconciler
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

    @MockK private lateinit var reconciler: StateReconciler

    private lateinit var pipelineCompletionHandler: PipelineCompletionHandler

    @BeforeEach
    fun setUp() {
        pipelineCompletionHandler =
            PipelineCompletionHandler(
                aggStore = aggStore,
                stateHistogramStore = stateHistogramStore,
                reconciler = reconciler
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
        val mockHistogram1 = mockk<PartitionHistogram>()
        val mockHistogram2 = mockk<PartitionHistogram>()

        val aggregateEntry1 =
            AggregateEntry(
                value = mockAggregate1,
                partitionHistogram = mockHistogram1,
                stalenessTrigger = mockk(),
                recordCountTrigger = mockk(),
                estimatedBytesTrigger = mockk()
            )

        val aggregateEntry2 =
            AggregateEntry(
                value = mockAggregate2,
                partitionHistogram = mockHistogram2,
                stalenessTrigger = mockk(),
                recordCountTrigger = mockk(),
                estimatedBytesTrigger = mockk()
            )

        every { aggStore.getAll() } returns listOf(aggregateEntry1, aggregateEntry2)
        coEvery { mockAggregate1.flush() } just Runs
        coEvery { mockAggregate2.flush() } just Runs
        every { stateHistogramStore.acceptFlushedCounts(any()) } returns mockk()
        coEvery { reconciler.disable() } just Runs
        every { reconciler.flushCompleteStates() } just Runs

        // When
        pipelineCompletionHandler.apply(null)

        // Then
        coVerify(exactly = 1) { mockAggregate1.flush() }
        coVerify(exactly = 1) { mockAggregate2.flush() }
        verify(exactly = 1) { stateHistogramStore.acceptFlushedCounts(mockHistogram1) }
        verify(exactly = 1) { stateHistogramStore.acceptFlushedCounts(mockHistogram2) }
        coVerify(exactly = 1) { reconciler.disable() }
        verify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    @Test
    fun `apply should handle empty aggregates list`() = runTest {
        // Given
        every { aggStore.getAll() } returns emptyList()
        coEvery { reconciler.disable() } just Runs
        every { reconciler.flushCompleteStates() } just Runs

        // When
        pipelineCompletionHandler.apply(null)

        // Then
        verify(exactly = 1) { aggStore.getAll() }
        coVerify(exactly = 1) { reconciler.disable() }
        verify(exactly = 1) { reconciler.flushCompleteStates() }
        verify(exactly = 0) { stateHistogramStore.acceptFlushedCounts(any()) }
    }

    @Test
    fun `apply should handle aggregate flush failure`() = runTest {
        // Given
        val mockAggregate = mockk<Aggregate>()
        val mockHistogram = mockk<PartitionHistogram>()
        val flushException = RuntimeException("Flush failed")

        val aggregateEntry =
            AggregateEntry(
                value = mockAggregate,
                partitionHistogram = mockHistogram,
                stalenessTrigger = mockk(),
                recordCountTrigger = mockk(),
                estimatedBytesTrigger = mockk()
            )

        every { aggStore.getAll() } returns listOf(aggregateEntry)
        coEvery { mockAggregate.flush() } throws flushException
        coEvery { reconciler.disable() } just Runs
        every { reconciler.flushCompleteStates() } just Runs

        // When & Then
        assertThrows<RuntimeException> { pipelineCompletionHandler.apply(null) }

        coVerify(exactly = 1) { mockAggregate.flush() }
        // Note: acceptFlushedCounts should not be called if flush fails
        verify(exactly = 0) { stateHistogramStore.acceptFlushedCounts(any()) }
    }
}
