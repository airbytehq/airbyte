/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderUploadCompleterStep<K : WithStream, T : RemoteObject<*>>(
    val objectLoader: ObjectLoader,
    val uploadCompleter: ObjectLoaderUploadCompleter<T>,
    @Named("objectLoaderLoadedPartQueue")
    val inputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
    @Named("objectLoaderCompletedUploadQueue")
    val completedUploadQueue:
        PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? =
        null,
    val completedUploadPartitioner: ObjectLoaderCompletedUploadPartitioner<K, T>? = null,
    val taskFactory: LoadPipelineStepTaskFactory,
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numUploadCompleters

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return if (completedUploadQueue == null) {
            taskFactory.createFinalStep(uploadCompleter, inputQueue, partition, numWorkers)
        } else {
            taskFactory.createIntermediateStep(
                uploadCompleter,
                inputQueue,
                completedUploadPartitioner!!,
                completedUploadQueue,
                partition,
                numWorkers,
                3
            )
        }
    }
}
