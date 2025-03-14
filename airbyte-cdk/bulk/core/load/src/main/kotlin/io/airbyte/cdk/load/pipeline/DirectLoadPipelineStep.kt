/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = DirectLoaderFactory::class)
class DirectLoadPipelineStep<S : DirectLoader>(
    val accumulator: DirectLoadRecordAccumulator<S, StreamKey>,
    @Named("recordQueue")
    val inputQueue: PartitionedQueue<Reserved<PipelineEvent<StreamKey, DestinationRecordRaw>>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
    @Value("\${airbyte.destination.core.record-batch-size-override:null}")
    val batchSizeOverride: Long? = null,
    val directLoaderFactory: DirectLoaderFactory<S>,
) : LoadPipelineStep {
    private val log = KotlinLogging.logger {}

    override val numWorkers: Int = directLoaderFactory.inputPartitions

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        log.info { "Creating DirectLoad pipeline step task for partition $partition" }
        return LoadPipelineStepTask(
            accumulator,
            inputQueue.consume(partition),
            batchUpdateQueue = batchQueue,
            outputPartitioner = null,
            outputQueue = null as PartitionedQueue<PipelineEvent<StreamKey, DirectLoadAccResult>>?,
            batchSizeOverride?.let { RecordCountFlushStrategy(it) },
            partition
        )
    }
}
