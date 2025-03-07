/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderUploadStep(
    val loader: ObjectLoader,
    val accumulator: ObjectLoaderPartToObjectAccumulator,
    @Named("objectLoaderPartQueue") val partQueue: PartitionedQueue<PipelineEvent<ObjectKey, Part>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
) : LoadPipelineStep {
    override val numWorkers: Int = loader.numUploadWorkers

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return LoadPipelineStepTask(
            accumulator,
            partQueue.consume(partition),
            batchQueue,
            outputPartitioner = null,
            outputQueue =
                null
                    as
                    PartitionedQueue<
                        PipelineEvent<StreamKey, ObjectLoaderPartToObjectAccumulator.ObjectResult>
                    >?,
            flushStrategy = null,
            partition
        )
    }
}
