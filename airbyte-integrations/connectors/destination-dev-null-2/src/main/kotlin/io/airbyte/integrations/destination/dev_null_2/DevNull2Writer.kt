/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

/**
 * Writer for Dev Null 2 destination. Creates no-op stream loaders since this destination discards
 * all data.
 */
@Singleton
class DevNull2Writer(
    private val config: DevNull2Configuration,
) : DestinationWriter {

    override suspend fun setup() {
        log.info { "DevNull2Writer setup - mode: ${config.type::class.simpleName}" }
        // No actual setup needed for dev-null destination
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        log.info {
            "Creating StreamLoader for stream: ${stream.mappedDescriptor.namespace}.${stream.mappedDescriptor.name}"
        }
        return DevNull2StreamLoader(stream)
    }
}

/** No-op StreamLoader for dev-null destination. All actual work happens in the Aggregate. */
class DevNull2StreamLoader(
    override val stream: DestinationStream,
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    override suspend fun start() {
        log.debug {
            "DevNull2StreamLoader start for stream: ${stream.mappedDescriptor.namespace}.${stream.mappedDescriptor.name}"
        }
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        log.debug {
            "DevNull2StreamLoader close for stream: ${stream.mappedDescriptor.namespace}.${stream.mappedDescriptor.name}, hadNonzeroRecords=$hadNonzeroRecords, failure=$streamFailure"
        }
    }
}
