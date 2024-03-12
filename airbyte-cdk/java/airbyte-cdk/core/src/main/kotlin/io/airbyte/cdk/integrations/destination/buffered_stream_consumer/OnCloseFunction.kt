/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.commons.functional.CheckedBiConsumer
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

/**
 * Async version of {@link
 * io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction}. Separately out
 * for easier versioning.
 */
fun interface OnCloseFunction :
    CheckedBiConsumer<Boolean, Map<StreamDescriptor, StreamSyncSummary>, Exception>

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
        u: Map<StreamDescriptor, StreamSyncSummary>,
    ) {
        logger.info { "Using default no-op implementation of on close function." }
    }
}
