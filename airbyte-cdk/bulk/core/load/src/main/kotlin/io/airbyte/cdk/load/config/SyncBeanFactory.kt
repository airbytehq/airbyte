/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.task.implementor.FileAggregateMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlin.math.min

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

    @Singleton
    @Named("fileAggregateQueue")
    fun fileAggregateQueue(
        @Value("\${airbyte.resources.disk.bytes}") availableBytes: Long,
        catalog: DestinationCatalog,
        config: DestinationConfiguration,
    ): MultiProducerChannel<FileAggregateMessage> {
        // total batches by disk capacity
        val maxBatchesThatFitOnDisk = (availableBytes / config.recordBatchSizeBytes).toInt()
        // account for batches in flight processing by the workers
        val maxBatchesMinusUploadOverhead = maxBatchesThatFitOnDisk - config.numProcessRecordsWorkers
        // ideally we'd allow enough headroom to smooth out rate differences between consumer / producer streams
        val idealDepth = 4 * config.numProcessRecordsWorkers
        // take the smaller of the two—this should be the idealDepth except in corner cases
        val capacity = min(maxBatchesMinusUploadOverhead, idealDepth)
        log.info { "Creating file aggregate queue with limit $capacity" }
        return MultiProducerChannel(capacity)
    }
}
