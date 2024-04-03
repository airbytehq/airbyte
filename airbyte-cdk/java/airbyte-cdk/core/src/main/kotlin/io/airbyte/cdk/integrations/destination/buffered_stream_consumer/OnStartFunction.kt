/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.commons.concurrency.VoidCallable
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

fun interface OnStartFunction : VoidCallable

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
