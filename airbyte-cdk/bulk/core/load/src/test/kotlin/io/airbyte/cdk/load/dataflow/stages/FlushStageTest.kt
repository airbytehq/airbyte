/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.mockk.coVerify
import io.mockk.mockk
import kotlin.test.assertSame
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class FlushStageTest {
    private val flushStage = FlushStage()

    @Test
    fun `given input with an aggregate, when apply is called, then it flushes the aggregate`() =
        runTest {
            // Given
            val mockAggregate = mockk<Aggregate>(relaxed = true)
            val input = DataFlowStageIO(aggregate = mockAggregate)

            // When
            val result = flushStage.apply(input)

            // Then
            coVerify(exactly = 1) { mockAggregate.flush() }
            assertSame(input, result, "The output should be the same instance as the input")
        }

    @Test
    fun `given input with a null aggregate, when apply is called, then it throws NullPointerException`() =
        runTest {
            // Given
            val input = DataFlowStageIO(aggregate = null)

            // When & Then
            assertThrows<NullPointerException> { flushStage.apply(input) }
        }
}
