/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.LimitedMessageQueue
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.task.implementor.FileQueueMessage
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
    @Named("spillFileQueue")
    fun spillFileQueue(
        @Value("\${airbyte.resources.disk.bytes}") availableBytes: Long,
        catalog: DestinationCatalog,
        config: DestinationConfiguration,
    ): LimitedMessageQueue<FileQueueMessage> {
        val maxNumberChunksInFlight = ((availableBytes / config.recordBatchSizeBytes) * 0.8).toInt()
        val minusOnePerStream = maxNumberChunksInFlight - catalog.streams.size
        val capacity = min(minusOnePerStream, 1)
        log.info { "Creating spill file queue with limit $capacity" }
        return LimitedMessageQueue(capacity)
    }
}
