package io.airbyte.cdk.core.destination.async.buffer

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class BufferMemory {
    companion object {
        const val MEMORY_LIMIT_RATIO: Double = 0.7
    }

    fun getMemoryLimit(): Long {
        return (Runtime.getRuntime().maxMemory() * MEMORY_LIMIT_RATIO).toLong()
    }
}
