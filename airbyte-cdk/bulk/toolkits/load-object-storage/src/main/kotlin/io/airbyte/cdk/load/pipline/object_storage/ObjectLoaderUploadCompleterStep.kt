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
class ObjectLoaderUploadCompleterStep(
    val objectLoader: ObjectLoader,
    val uploadCompleter: ObjectLoaderUploadCompleter,
    @Named("objectLoaderLoadedPartQueue")
    val inputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult>>,
    val taskFactory: LoadPipelineStepTaskFactory
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numUploadCompleters

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createFinalStep(
            uploadCompleter,
            inputQueue,
            partition,
            numWorkers,
        )
    }
}
