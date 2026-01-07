/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class DevNullV2Writer : DestinationWriter {
    private val log = KotlinLogging.logger {}
    
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        log.info { "Creating StreamLoader for stream: ${stream.unmappedDescriptor}" }
        
        // For dev-null, we create a minimal StreamLoader that does nothing
        // The actual work is done by the Aggregate which discards records
        return DevNullV2StreamLoader(stream)
    }
}

/**
 * Minimal StreamLoader implementation for dev-null.
 * Since dev-null doesn't persist data, all operations are no-ops.
 */
class DevNullV2StreamLoader(
    override val stream: DestinationStream
) : StreamLoader {
    private val log = KotlinLogging.logger {}
    
    override suspend fun start() {
        log.info { "Starting stream loader for ${stream.unmappedDescriptor} (no-op)" }
    }
    
    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        log.info { "Closing stream loader for ${stream.unmappedDescriptor} (no-op)" }
    }
}