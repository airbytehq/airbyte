/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.LoadedObject
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = BulkLoaderFactory::class)
class BulkLoadIntoTableStep<K : WithStream, T : RemoteObject<*>>(
    val bulkLoadAccumulator: BulkLoadAccumulator<K, T>,
    val bulkLoad: BulkLoaderFactory<K, T>,
    @Named("objectLoaderOutputQueue")
    val bulkLoadObjectQueue: PartitionedQueue<PipelineEvent<K, LoadedObject<T>>>,
    @Named("batchStateUpdateQueue") val batchUpdateQueue: QueueWriter<BatchUpdate>,
) : LoadPipelineStep {
    override val numWorkers: Int = bulkLoad.maxNumConcurrentLoads

    /** TODO: This should just be a task: no need for a whole accumulator pipeline here */
    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return LoadPipelineStepTask(
            bulkLoadAccumulator,
            bulkLoadObjectQueue.consume(partition),
            batchUpdateQueue,
            null,
            null as PartitionedQueue<PipelineEvent<K, BulkLoadAccumulator.LoadResult>>?,
            null,
            partition
        )
    }
}
