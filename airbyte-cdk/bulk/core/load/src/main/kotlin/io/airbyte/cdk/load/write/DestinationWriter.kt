/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Implementor interface. Every Destination must extend this and at least provide an implementation
 * of [createStreamLoader].
 */
interface DestinationWriter {
    // Called once before anything else
    suspend fun setup() {}

    // Return a StreamLoader for the given stream
    fun createStreamLoader(stream: DestinationStream): StreamLoader

    // Called once at the end of the job, unconditionally.
    // NOTE: we don't pass Success here, because it depends on this completing successfully.
    suspend fun teardown(destinationFailure: DestinationFailure? = null) {}
}

@Singleton
@Secondary
class DefaultDestinationWriter : DestinationWriter {
    init {
        throw NotImplementedError(
            "DestinationWrite not implemented. Please create a custom @Singleton implementation."
        )
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        throw NotImplementedError()
    }
}
