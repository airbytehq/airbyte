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
import java.util.concurrent.atomic.AtomicLong

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderUploadCompleterStep(
    val objectLoader: ObjectLoader,
    val uploadCompleter: ObjectLoaderUploadCompleter,
    @Named("objectLoaderLoadedPartQueue")
    val inputQueue: PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numUploadCompleters
    private val streamCompletionMap = ConcurrentHashMap<DestinationStream.Descriptor, AtomicLong>()

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return LoadPipelineStepTask(
            uploadCompleter,
            inputQueue.consume(partition),
            batchQueue,
            null,
            null
                as
                PartitionedQueue<
                    PipelineEvent<ObjectKey, ObjectLoaderUploadCompleter.UploadResult>>?,
            null,
            partition,
            numWorkers,
            streamCompletionMap
        )
    }
}
