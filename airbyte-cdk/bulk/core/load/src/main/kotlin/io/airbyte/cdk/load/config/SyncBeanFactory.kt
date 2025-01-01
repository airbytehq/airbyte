/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.task.implementor.FileAggregateMessage
import io.airbyte.cdk.load.task.implementor.FileTransferQueueMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlin.math.min
import kotlinx.coroutines.channels.Channel

/** Factory for instantiating beans necessary for the sync process. */
@Factory
class SyncBeanFactory {
    private val log = KotlinLogging.logger {}

    @Singleton
    @Named("memoryManager")
    fun memoryManager(
        config: DestinationConfiguration,
    ): ReservationManager {
        val memory = config.maxMessageQueueMemoryUsageRatio * Runtime.getRuntime().maxMemory()

        return ReservationManager(memory.toLong())
    }

    @Singleton
    @Named("diskManager")
    fun diskManager(
        @Value("\${airbyte.resources.disk.bytes}") availableBytes: Long,
    ): ReservationManager {
        return ReservationManager(availableBytes)
    }

    /**
     * The queue that sits between the aggregation (SpillToDiskTask) and load steps
     * (ProcessRecordsTask).
     *
     * Since we are buffering on disk, we must consider the available disk space in our depth
     * configuration.
     */
    @Singleton
    @Named("fileAggregateQueue")
    fun fileAggregateQueue(
        @Value("\${airbyte.resources.disk.bytes}") availableBytes: Long,
        config: DestinationConfiguration,
        catalog: DestinationCatalog
    ): MultiProducerChannel<FileAggregateMessage> {
        val streamCount = catalog.size()
        // total batches by disk capacity
        val maxBatchesThatFitOnDisk = (availableBytes / config.recordBatchSizeBytes).toInt()
        // account for batches in flight processing by the workers
        val maxBatchesMinusUploadOverhead =
            maxBatchesThatFitOnDisk - config.numProcessRecordsWorkers
        // ideally we'd allow enough headroom to smooth out rate differences between consumer /
        // producer streams
        val idealDepth = 4 * config.numProcessRecordsWorkers
        // take the smaller of the two—this should be the idealDepth except in corner cases
        val capacity = min(maxBatchesMinusUploadOverhead, idealDepth)
        log.info { "Creating file aggregate queue with limit $capacity" }
        val channel = Channel<FileAggregateMessage>(capacity)
        return MultiProducerChannel(streamCount.toLong(), channel, "fileAggregateQueue")
    }

    @Singleton
    @Named("batchQueue")
    fun batchQueue(
        config: DestinationConfiguration,
    ): MultiProducerChannel<BatchEnvelope<*>> {
        val channel = Channel<BatchEnvelope<*>>(config.batchQueueDepth)
        return MultiProducerChannel(config.numProcessRecordsWorkers.toLong(), channel, "batchQueue")
    }

    @Singleton
    @Named("fileMessageQueue")
    fun fileMessageQueue(
        config: DestinationConfiguration,
    ): MultiProducerChannel<FileTransferQueueMessage> {
        val channel = Channel<FileTransferQueueMessage>(config.batchQueueDepth)
        return MultiProducerChannel(1, channel, "fileMessageQueue")
    }
}
