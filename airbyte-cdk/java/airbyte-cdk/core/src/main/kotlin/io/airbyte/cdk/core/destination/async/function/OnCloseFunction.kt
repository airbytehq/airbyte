package io.airbyte.cdk.core.destination.async.function

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.function.BiConsumer

private val logger = KotlinLogging.logger {}

/**
 * Async version of
 * {@link io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction}.
 * Separately out for easier versioning.
 */
interface OnCloseFunction :
    BiConsumer<Boolean, MutableMap<StreamDescriptor, StreamSyncSummary>>

@Singleton
@Named("onCloseFunction")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class DefaultOnCloseFunction : OnCloseFunction {
    override fun accept(
        t: Boolean,
        u: MutableMap<StreamDescriptor, StreamSyncSummary>,
    ) {
        logger.info { "Using default no-op implementation of on close function." }
    }
}
