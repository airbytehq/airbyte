/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipeline.RecordCountFlushStrategy
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartFormatterStep(
    private val objectLoader: ObjectLoader,
    private val recordToPartAccumulator: ObjectLoaderPartFormatter<*>,
    @Named("recordQueue")
    val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
    @Named("objectLoaderPartQueue")
    val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    @Value("\${airbyte.destination.core.record-batch-size-override:null}")
    val batchSizeOverride: Long? = null,
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numPartWorkers
    private val streamCompletionMap = ConcurrentHashMap<DestinationStream.Descriptor, AtomicLong>()

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return LoadPipelineStepTask(
            recordToPartAccumulator,
            inputQueue.consume(partition),
            batchQueue,
            ObjectLoaderFormattedPartPartitioner(),
            outputQueue,
            batchSizeOverride?.let { RecordCountFlushStrategy(it) },
            partition,
            numWorkers,
            streamCompletionMap
        )
    }
}
