/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.mockk.mockk
import io.mockk.verify
import kotlin.test.assertFailsWith
import kotlin.test.assertSame
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class StateStageTest {
    private val stateStore: StateHistogramStore = mockk(relaxed = true)
    private lateinit var stateStage: StateStage

    @BeforeEach
    fun setup() {
        stateStage = StateStage(stateStore)
    }

    @Test
    fun `apply happy path`() = runTest {
        // Arrange
        val countsHistogram = mockk<PartitionHistogram>()
        val bytesHistogram = mockk<PartitionHistogram>()
        val input =
            DataFlowStageIO(
                partitionCountsHistogram = countsHistogram,
                partitionBytesHistogram = bytesHistogram,
            )

        // Act
        val result = stateStage.apply(input)

        // Assert
        verify(exactly = 1) { stateStore.acceptFlushedCounts(countsHistogram) }
        verify(exactly = 1) { stateStore.acceptFlushedBytes(bytesHistogram) }
        assertSame(input, result, "The output should be the same as the input object")
    }

    @Test
    fun `apply with null counts histogram throws exception`() = runTest {
        val input = DataFlowStageIO(partitionCountsHistogram = null)
        assertFailsWith<NullPointerException> { stateStage.apply(input) }
        verify(exactly = 0) { stateStore.acceptFlushedCounts(any()) }
    }

    @Test
    fun `apply with null bytes histogram throws exception`() = runTest {
        val input = DataFlowStageIO(partitionBytesHistogram = null)
        assertFailsWith<NullPointerException> { stateStage.apply(input) }
        verify(exactly = 0) { stateStore.acceptFlushedBytes(any()) }
    }
}
