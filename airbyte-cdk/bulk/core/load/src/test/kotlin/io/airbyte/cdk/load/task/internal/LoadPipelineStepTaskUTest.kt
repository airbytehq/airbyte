/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.state.Reserved
import io.mockk.impl.annotations.MockK
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class LoadPipelineStepTaskUTest {
    @MockK lateinit var batchAccumulator: BatchAccumulator<StreamKey, AutoCloseable, String, String>
    @MockK lateinit var inputFlow: Flow<Reserved<PipelineEvent<StreamKey, String>>>
    @MockK lateinit var batchUpdateQueue: QueueWriter<BatchUpdate>
    @MockK lateinit var outputPartitioner: OutputPartitioner<StreamKey, String, StreamKey, String>
    @MockK lateinit var outputQueue: PartitionedQueue<PipelineEvent<StreamKey, String>>
    @MockK lateinit var flushStrategy: PipelineFlushStrategy

    class Closeable : AutoCloseable {
        override fun close() {}
    }

    private fun createTask(
        part: Int
    ): LoadPipelineStepTask<AutoCloseable, StreamKey, String, StreamKey, String> =
        LoadPipelineStepTask(
            batchAccumulator,
            inputFlow,
            batchUpdateQueue,
            outputPartitioner,
            outputQueue,
            flushStrategy,
            part
        )

    @Test fun `start and accept called on first key`() = runTest {}
}
