/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.state.ReservationManager
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

/** Factory for instantiating beans necessary for the sync process. */
@Factory
class SyncBeanFactory {
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
}
