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
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.dlq.DlqLoader

/**
 * DeadLetterQueue Loader Pipeline Step.
 *
 * This is the first step of the dead letter queue pipeline that will wrap the destination
 * implementer code.
 */
class DlqLoaderPipelineStep<S : AutoCloseable>(
    override val numWorkers: Int,
    private val taskFactory: LoadPipelineStepTaskFactory,
    private val dlqLoader: DlqLoader<S>,
    private val outputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val deadLetterQueueEnabled: Boolean,
) : LoadPipelineStep {
    override fun taskForPartition(partition: Int): Task {
        return taskFactory.createFirstStep(
            batchAccumulator = DlqLoaderAccumulator(dlqLoader, deadLetterQueueEnabled),
            outputPartitioner = PassThroughPartitioner(),
            outputQueue = FlattenQueueAdapter(outputQueue),
            part = partition,
            numWorkers = numWorkers,
        )
    }
}

/**
 * Part of the BatchAccumulator interface.
 * - This implements [WithBatchState] in order to control checkpointing.
 * - [rejectedRecords] are records meant for the DeadLetterQueue.
 */
class DlqStepOutput(
    override val state: BatchState,
    val rejectedRecords: List<DestinationRecordRaw>? = null,
) : WithBatchState

/** Wraps a [DlqLoader] into a [BatchAccumulator] so that it fits into a [LoadPipeline]. */
class DlqLoaderAccumulator<S>(
    private val loader: DlqLoader<S>,
    private val deadLetterQueueEnabled: Boolean,
) : BatchAccumulator<S, StreamKey, DestinationRecordRaw, DlqStepOutput> {
    /** Propagates the call to the [DlqLoader] in order to create a new state for a stream. */
    override suspend fun start(key: StreamKey, part: Int): S = loader.start(key, part)

    /**
     * Propagates the accept call to the [DlqLoader].
     *
     * If the [DlqLoader] returns:
     * - [DlqLoader.Incomplete]: it assumes that no data was persisted, and continue with the
     * current state.
     * - [DlqLoader.Complete]: it assumes that data was at least partially persisted. If no records
     * are returned, it means that the upload was successful, the batch is complete since there are
     * no data to write to the dead letter queue. The CDK should be able to persist the
     * AirbyteState. On the other hand, if records are returned, they are sent to the
     * DeadLetterQueue and the BatchState is PERSISTED in order to let the CDK know that it
     * shouldn't ack the AirbyteState until those records are persisted in the DeadLetterQueue.
     */
    override suspend fun accept(
        input: DestinationRecordRaw,
        state: S,
    ): BatchAccumulatorResult<S, DlqStepOutput> {
        return when (val result = loader.accept(input, state)) {
            is DlqLoader.Incomplete -> NoOutput(state)
            is DlqLoader.Complete -> FinalOutput(getOutput(result.rejectedRecords))
        }
    }

    override suspend fun finish(state: S): FinalOutput<S, DlqStepOutput> {
        val result = loader.finish(state)
        return FinalOutput(getOutput(result.rejectedRecords))
    }

    private fun getOutput(rejectedRecords: List<DestinationRecordRaw>?) =
        if (deadLetterQueueEnabled) {
            when (rejectedRecords) {
                null -> DlqStepOutput(BatchState.COMPLETE, null)
                else -> DlqStepOutput(BatchState.PERSISTED, rejectedRecords)
            }
        } else {
            // Because Dead Letter Queue is disable, we never return rejected records.
            // TODO: count rejected records for stats reporting
            DlqStepOutput(BatchState.COMPLETE, null)
        }
}
