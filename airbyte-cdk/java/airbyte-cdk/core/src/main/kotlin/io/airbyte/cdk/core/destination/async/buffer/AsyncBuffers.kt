package io.airbyte.cdk.core.destination.async.buffer

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class AsyncBuffers {
    val buffers: ConcurrentMap<StreamDescriptor, StreamAwareQueue> = ConcurrentHashMap()
}
