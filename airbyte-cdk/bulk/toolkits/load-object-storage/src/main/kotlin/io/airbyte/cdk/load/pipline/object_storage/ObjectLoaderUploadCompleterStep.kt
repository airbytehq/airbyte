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

class ObjectLoaderUploadCompleterStep<K : WithStream, T : RemoteObject<*>>(
    objectLoader: ObjectLoader,
    private val uploadCompleter: ObjectLoaderUploadCompleter<T>,
    private val inputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<T>>>,
    private val completedUploadQueue:
        PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? =
        null,
    private val completedUploadPartitioner:
        ObjectLoaderCompletedUploadPartitioner<
            ObjectKey, ObjectLoaderPartLoader.PartResult<T>, K, T>? =
        null,
    private val taskFactory: LoadPipelineStepTaskFactory,
    private val stepId: String,
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numUploadCompleters

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return if (completedUploadQueue == null) {
            taskFactory.createFinalStep(uploadCompleter, inputQueue, partition, numWorkers)
        } else {
            taskFactory.createIntermediateStep(
                uploadCompleter,
                inputQueue.consume(partition),
                completedUploadPartitioner,
                completedUploadQueue,
                partition,
                numWorkers,
                stepId = stepId,
            )
        }
    }
}
