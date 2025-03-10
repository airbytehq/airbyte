/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
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

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartStep(
    private val objectLoader: ObjectLoader,
    private val recordToPartAccumulator: ObjectLoaderRecordToPartAccumulator<*>,
    @Named("recordQueue")
    val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordAirbyteValue>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
    @Named("objectLoaderPartQueue") val partQueue: PartitionedQueue<PipelineEvent<ObjectKey, Part>>,
    @Value("\${airbyte.destination.core.record-batch-size-override:null}")
    val batchSizeOverride: Long? = null,
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numPartWorkers

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return LoadPipelineStepTask(
            recordToPartAccumulator,
            inputQueue.consume(partition),
            batchQueue,
            ObjectLoaderPartPartitioner(),
            partQueue,
            batchSizeOverride?.let { RecordCountFlushStrategy(it) },
            partition
        )
    }
}
