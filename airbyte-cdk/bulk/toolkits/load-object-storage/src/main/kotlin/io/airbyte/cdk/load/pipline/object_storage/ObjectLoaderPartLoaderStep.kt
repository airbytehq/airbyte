/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader

class ObjectLoaderPartLoaderStep<T : RemoteObject<*>>(
    loader: ObjectLoader,
    private val partLoader: ObjectLoaderPartLoader<T>,
    private val inputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
    private val taskFactory: LoadPipelineStepTaskFactory,
    private val stepId: String,
) : LoadPipelineStep {
    override val numWorkers: Int = loader.numUploadWorkers

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createIntermediateStep(
            partLoader,
            inputQueue.consume(partition),
            outputPartitioner = ObjectLoaderLoadedPartPartitioner(),
            outputQueue,
            partition,
            numWorkers,
            stepId = stepId,
        )
    }
}
