/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.dlq

import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory

/**
 * Define a NoopStep for the Dead Letter Queue.
 *
 * This step skips through all records without doing anything. This is to make sure we update the
 * counts of rejected records properly by leveraging the [FlattenQueueAdapter] and the fact that the
 * LoadPipelineStepTask will update the rejected records count correctly on [BatchState.COMPLETE].
 */
class DlqNoopPipelineStep(
    override val numWorkers: Int,
    private val taskFactory: LoadPipelineStepTaskFactory,
    private val dlqInputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
) : LoadPipelineStep {
    override fun taskForPartition(partition: Int): Task {
        return taskFactory.createFinalStep(
            batchAccumulator = DlqNoopAccumulator(),
            inputQueue = dlqInputQueue,
            part = partition,
            numWorkers = numWorkers,
        )
    }
}

/** See documentation of [DlqNoopPipelineStep]. */
class DlqNoopAccumulator :
    BatchAccumulator<DlqNoopState, StreamKey, DestinationRecordRaw, WithBatchState> {
    override suspend fun start(key: StreamKey, part: Int): DlqNoopState = DlqNoopState()

    override suspend fun accept(
        input: DestinationRecordRaw,
        state: DlqNoopState
    ): BatchAccumulatorResult<DlqNoopState, WithBatchState> = FinalOutput(DlqNoopState())

    override suspend fun finish(state: DlqNoopState): FinalOutput<DlqNoopState, WithBatchState> =
        FinalOutput(DlqNoopState())
}

/** See documentation of [DlqNoopPipelineStep]. */
class DlqNoopState : WithBatchState, AutoCloseable {
    override val state: BatchState = BatchState.COMPLETE
    override fun close() {}
}
