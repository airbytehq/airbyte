package io.airbyte.cdk.core.destination.async.function

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.commons.concurrency.VoidCallable
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

interface OnStartFunction : VoidCallable

@Singleton
@Named("onStartFunction")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class DefaultOnStartFunction : OnStartFunction {
    override fun voidCall() {
        logger.info { "Using default no-op implementation of on start function." }
    }
}
