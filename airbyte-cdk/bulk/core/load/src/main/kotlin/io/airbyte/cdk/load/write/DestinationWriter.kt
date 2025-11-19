/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Main entry point for destination connectors that orchestrates the loading lifecycle.
 *
 * Every destination must implement this interface to handle setup, stream loader creation, and
 * teardown operations. The framework calls these methods in a specific order:
 * 1. [setup]
 * - Initialize destination resources (connections, temp directories, etc.)
 * 2. [createStreamLoader]
 * - Create a loader for each stream being synced
 * 3. [teardown]
 * - Clean up resources after all streams complete
 */
interface DestinationWriter {
    /**
     * Initializes destination-level resources before any streams are processed.
     *
     * Called once at the start of the sync. Use this to establish database connections, create
     * temporary directories, or perform other one-time setup operations.
     */
    suspend fun setup() {}

    /**
     * Creates a stream-specific loader to handle data for the given stream.
     *
     * Called once per stream at the start of processing. The returned [StreamLoader] will receive
     * all records for this stream and manage table operations.
     *
     * @param stream The stream configuration including schema and sync mode
     * @return A [StreamLoader] instance to handle this stream's data
     */
    fun createStreamLoader(stream: DestinationStream): StreamLoader

    /**
     * Cleans up destination-level resources after all streams have completed.
     *
     * Called once at the end of the sync, regardless of success or failure. Use this to close
     * database connections, delete temporary files, or perform other cleanup.
     *
     * @param destinationFailure If present, indicates the sync failed with this error
     */
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
