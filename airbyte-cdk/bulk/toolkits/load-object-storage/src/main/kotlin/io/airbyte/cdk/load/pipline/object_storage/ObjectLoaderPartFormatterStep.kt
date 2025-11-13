/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import kotlinx.coroutines.flow.Flow

class ObjectLoaderPartFormatterStep(
    override val numWorkers: Int,
    private val partFormatter: ObjectLoaderPartFormatter<*>,
    private val inputFlows: Array<Flow<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
    private val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val taskFactory: LoadPipelineStepTaskFactory,
    private val stepId: String,
    private val flushStrategy: PipelineFlushStrategy?,
) : LoadPipelineStep {

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.create(
            partFormatter,
            inputFlows[partition],
            ObjectLoaderFormattedPartPartitioner(),
            outputQueue,
            flushStrategy,
            partition,
            numWorkers,
            stepId = stepId,
        )
    }
}
