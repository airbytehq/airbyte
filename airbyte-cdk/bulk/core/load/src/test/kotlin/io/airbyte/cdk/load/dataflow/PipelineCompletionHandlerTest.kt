/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateEntry
import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.aggregate.SizeTrigger
import io.airbyte.cdk.load.dataflow.aggregate.TimeTrigger
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.RelaxedMockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class PipelineCompletionHandlerTest {
    @RelaxedMockK private lateinit var aggStore: AggregateStore

    @RelaxedMockK private lateinit var stateWatermarkStore: StateStore

    @RelaxedMockK private lateinit var reconciler: StateReconciler

    private lateinit var handler: PipelineCompletionHandler

    @BeforeEach
    fun setup() {
        handler = PipelineCompletionHandler(aggStore, stateWatermarkStore, reconciler)
    }

    @Test
    fun `test apply with exception`() = runTest {
        val exception = RuntimeException("test exception")

        assertThrows<RuntimeException> { handler.apply(exception) }
    }

    @Test
    fun `test apply successful completion`() = runTest {
        val aggregator1 = mockk<Aggregate>(relaxed = true)
        val histogram1 = PartitionHistogram()
        val entry1 = createAggregateEntry(aggregator1, histogram1)

        val aggregator2 = mockk<Aggregate>(relaxed = true)
        val histogram2 = PartitionHistogram()
        val entry2 = createAggregateEntry(aggregator2, histogram2)

        every { aggStore.getAll() } returns listOf(entry1, entry2)

        handler.apply(null)

        coVerify(exactly = 1) { aggregator1.flush() }
        coVerify(exactly = 1) { aggregator2.flush() }
        coVerify(exactly = 1) { stateWatermarkStore.acceptFlushedCounts(histogram1) }
        coVerify(exactly = 1) { stateWatermarkStore.acceptFlushedCounts(histogram2) }
        coVerify(exactly = 1) { reconciler.disable() }
        coVerify(exactly = 1) { reconciler.flushCompleteStates() }
    }

    private fun createAggregateEntry(
        aggregator: Aggregate,
        histogram: PartitionHistogram,
    ): AggregateEntry =
        AggregateEntry(
            value = aggregator,
            partitionHistogram = histogram,
            stalenessTrigger = TimeTrigger(Long.MAX_VALUE),
            recordCountTrigger = SizeTrigger(Long.MAX_VALUE),
            estimatedBytesTrigger = SizeTrigger(Long.MAX_VALUE),
        )
}
