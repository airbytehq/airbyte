/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.buffers

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
open class BufferMemory {
    companion object {
        const val MEMORY_LIMIT_RATIO: Double = 0.7
    }

    open fun getMemoryLimit(): Long {
        return (Runtime.getRuntime().maxMemory() * MEMORY_LIMIT_RATIO).toLong()
    }
}
