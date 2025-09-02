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
        val histogram = mockk<PartitionHistogram>()
        val input = DataFlowStageIO(partitionHistogram = histogram)

        // Act
        val result = stateStage.apply(input)

        // Assert
        verify(exactly = 1) { stateStore.acceptFlushedCounts(histogram) }
        assertSame(input, result, "The output should be the same as the input object")
    }

    @Test
    fun `apply with null partition histogram throws exception`() = runTest {
        val input = DataFlowStageIO(partitionHistogram = null)
        assertFailsWith<NullPointerException> { stateStage.apply(input) }
        verify(exactly = 0) { stateStore.acceptFlushedCounts(any()) }
    }
}
