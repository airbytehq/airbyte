/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.config

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.state.MemoryManager
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

/** Factory for instantiating beans necessary for the sync process. */
@Factory
class SyncBeanFactory {
    @Singleton
    fun memoryManager(
        config: DestinationConfiguration,
    ): MemoryManager {
        val memory = config.maxMessageQueueMemoryUsageRatio * Runtime.getRuntime().maxMemory()

        return MemoryManager(memory.toLong())
    }
}
