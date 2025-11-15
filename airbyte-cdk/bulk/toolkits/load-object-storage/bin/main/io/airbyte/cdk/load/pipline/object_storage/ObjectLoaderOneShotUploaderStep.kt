/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory

class ObjectLoaderOneShotUploaderStep<K : WithStream, T : RemoteObject<*>>(
    private val objectLoaderOneShotUploader: ObjectLoaderOneShotUploader<*, T>,
    private val completedUploadQueue:
        PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>? =
        null,
    private val completedUploadPartitioner:
        ObjectLoaderCompletedUploadPartitioner<StreamKey, DestinationRecordRaw, K, T>? =
        null,
    private val taskFactory: LoadPipelineStepTaskFactory,
    override val numWorkers: Int
) : LoadPipelineStep {
    override fun taskForPartition(partition: Int): Task {
        return taskFactory.createFirstStep(
            objectLoaderOneShotUploader,
            completedUploadPartitioner,
            completedUploadQueue,
            partition,
            numWorkers,
            null
        )
    }
}
