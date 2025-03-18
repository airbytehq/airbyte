/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartLoaderStep(
    val loader: ObjectLoader,
    val accumulator: ObjectLoaderPartLoader,
    @Named("objectLoaderPartQueue")
    val inputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    @Named("objectLoaderLoadedPartQueue")
    val outputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
) : LoadPipelineStep {
    override val numWorkers: Int = loader.numUploadWorkers
    private val streamCompletionMap =
        ConcurrentHashMap<DestinationStream.Descriptor, AtomicInteger>()

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return LoadPipelineStepTask(
            accumulator,
            inputQueue.consume(partition),
            batchQueue,
            outputPartitioner = ObjectLoaderLoadedPartPartitioner(),
            outputQueue = outputQueue,
            flushStrategy = null,
            partition,
            numWorkers,
            streamCompletionMap
        )
    }
}
