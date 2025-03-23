/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = BulkLoaderFactory::class)
class BulkLoaderLoadIntoTableStep<K : WithStream, T : RemoteObject<*>>(
    val bulkLoader: BulkLoaderFactory<K, T>,
    val tableLoader: BulkLoaderTableLoader<K, T>,
    @Named("objectLoaderCompletedUploadQueue")
    val inputQueue: PartitionedQueue<PipelineEvent<K, ObjectLoaderUploadCompleter.UploadResult<T>>>,
    val taskFactory: LoadPipelineStepTaskFactory,
) : LoadPipelineStep {
    override val numWorkers: Int = bulkLoader.maxNumConcurrentLoads
    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createFinalStep(tableLoader, inputQueue, partition, numWorkers)
    }
}
