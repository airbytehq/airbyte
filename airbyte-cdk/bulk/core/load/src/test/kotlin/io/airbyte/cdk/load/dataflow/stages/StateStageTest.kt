/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.airbyte.cdk.load.dataflow.state.stats.CommittedStatsStore
import io.mockk.mockk
import io.mockk.verify
import kotlin.test.assertSame
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class StateStageTest {
    private val stateStore: StateHistogramStore = mockk(relaxed = true)
    private val statsStore: CommittedStatsStore = mockk(relaxed = true)
    private lateinit var stateStage: StateStage

    @BeforeEach
    fun setup() {
        stateStage = StateStage(stateStore, statsStore)
    }

    @Test
    fun `apply happy path`() = runTest {
        // Arrange
        val countsHistogram = mockk<PartitionHistogram>()
        val bytesHistogram = mockk<PartitionHistogram>()
        val desc = DestinationStream.Descriptor("namespace", "stream")
        val input =
            DataFlowStageIO(
                partitionCountsHistogram = countsHistogram,
                partitionBytesHistogram = bytesHistogram,
                mappedDesc = desc,
            )

        // Act
        val result = stateStage.apply(input)

        // Assert
        verify(exactly = 1) { stateStore.acceptFlushedCounts(countsHistogram) }
        verify(exactly = 1) { statsStore.acceptStats(desc, countsHistogram, bytesHistogram) }
        assertSame(input, result, "The output should be the same as the input object")
    }
}
