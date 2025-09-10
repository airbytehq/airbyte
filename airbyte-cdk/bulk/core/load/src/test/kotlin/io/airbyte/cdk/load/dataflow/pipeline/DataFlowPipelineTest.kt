/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.airbyte.cdk.load.dataflow.stages.AggregateStage
import io.mockk.coEvery
import io.mockk.coVerifySequence
import io.mockk.mockk
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

@ExperimentalCoroutinesApi
class DataFlowPipelineTest {
    private val parse = mockk<DataFlowStage>()
    private val aggregate = mockk<AggregateStage>()
    private val flush = mockk<DataFlowStage>()
    private val state = mockk<DataFlowStage>()
    private val completionHandler = mockk<PipelineCompletionHandler>()
    private val memoryAndParallelismConfig =
        MemoryAndParallelismConfig(
            maxOpenAggregates = 2,
            maxBufferedAggregates = 2,
        )

    @Test
    fun `pipeline execution flow`() = runTest {
        // Given
        val initialIO = mockk<DataFlowStageIO>()
        val input = flowOf(initialIO)
        val pipeline =
            DataFlowPipeline(
                input,
                parse,
                aggregate,
                flush,
                state,
                completionHandler,
                memoryAndParallelismConfig
            )

        val parsedIO = mockk<DataFlowStageIO>()
        val aggregatedIO = mockk<DataFlowStageIO>()
        val flushedIO = mockk<DataFlowStageIO>()
        val stateIO = mockk<DataFlowStageIO>()

        coEvery { parse.apply(initialIO) } returns parsedIO
        coEvery { aggregate.apply(parsedIO, any()) } coAnswers
            {
                val collector = secondArg<kotlinx.coroutines.flow.FlowCollector<DataFlowStageIO>>()
                collector.emit(aggregatedIO)
            }
        coEvery { flush.apply(aggregatedIO) } returns flushedIO
        coEvery { state.apply(flushedIO) } returns stateIO
        coEvery { completionHandler.apply(null) } returns Unit

        // When
        pipeline.run()

        // Then
        coVerifySequence {
            parse.apply(initialIO)
            aggregate.apply(parsedIO, any())
            flush.apply(aggregatedIO)
            state.apply(flushedIO)
            completionHandler.apply(null)
        }
    }
}
