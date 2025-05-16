/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import kotlinx.coroutines.flow.Flow

class ObjectLoaderPartFormatterStep(
    objectLoader: ObjectLoader,
    private val partFormatter: ObjectLoaderPartFormatter<*>,
    private val inputFlows: Array<Flow<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
    private val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val taskFactory: LoadPipelineStepTaskFactory,
    private val stepId: String,
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numPartWorkers

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createIntermediateStep(
            partFormatter,
            inputFlows[partition],
            ObjectLoaderFormattedPartPartitioner(),
            outputQueue,
            partition,
            numWorkers,
            stepId = stepId,
        )
    }
}
