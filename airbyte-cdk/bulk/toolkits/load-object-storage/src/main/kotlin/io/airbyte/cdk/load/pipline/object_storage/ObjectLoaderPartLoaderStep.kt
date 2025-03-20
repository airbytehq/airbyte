/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartLoaderStep(
    val loader: ObjectLoader,
    val partLoader: ObjectLoaderPartLoader,
    @Named("objectLoaderPartQueue")
    val inputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    @Named("objectLoaderLoadedPartQueue")
    val outputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult>>,
    val taskFactory: LoadPipelineStepTaskFactory,
) : LoadPipelineStep {
    override val numWorkers: Int = loader.numUploadWorkers

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createIntermediateStep(
            partLoader,
            inputQueue,
            ObjectLoaderLoadedPartPartitioner(),
            outputQueue,
            partition,
            numWorkers,
            taskIndex = 2
        )
    }
}
