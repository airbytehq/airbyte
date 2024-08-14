/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.command.DestinationStream
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Implementor interface. Extended this only if you need to perform initialization and teardown
 * *across all streams*, or if your per-stream operations need shared global state.
 *
 * If initialization can be done on a per-stream basis, implement @[StreamLoaderFactory] instead.
 */
interface Destination {
    // Called once before anything else
    suspend fun setup() {}

    // Return a StreamLoader for the given stream
    fun getStreamLoader(stream: DestinationStream): StreamLoader

    // Called once at the end of the job
    suspend fun teardown(succeeded: Boolean = true) {}
}

@Singleton
@Secondary
class DefaultDestination(private val streamLoaderFactory: StreamLoaderFactory) : Destination {
    override fun getStreamLoader(stream: DestinationStream): StreamLoader {
        return streamLoaderFactory.make(stream)
    }
}
