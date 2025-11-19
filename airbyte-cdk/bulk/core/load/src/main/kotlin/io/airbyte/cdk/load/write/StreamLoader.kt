/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed

/**
 * Per-stream handler that manages the loading lifecycle for a single data stream.
 *
 * Each stream gets its own loader instance to handle table creation, data loading, and
 * finalization. The framework calls these methods in order:
 * 1. [start]
 * - Initialize stream resources (create tables, open buffers)
 * 2. Records are processed (handled by the framework)
 * 3. [close] or [teardown]
 * - Finalize the stream (commit data, drop temp tables)
 */
interface StreamLoader {
    /** The stream configuration this loader handles. */
    val stream: DestinationStream

    /**
     * Initializes stream-specific resources before processing records.
     *
     * Called once at the start of stream processing. Use this to create destination tables,
     * allocate buffers, or perform other stream-level setup.
     */
    suspend fun start() {}

    /**
     * Finalizes the stream after all records have been processed.
     *
     * Called once after record processing completes, regardless of success or failure. Use this to
     * commit buffered data, merge staging tables, or clean up resources.
     *
     * @param hadNonzeroRecords True if at least one record was processed for this stream
     * @param streamFailure If present, indicates processing failed with this error
     */
    suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed? = null) {}

    /**
     * Simplified finalization API that delegates to [close].
     *
     * Provides a boolean success flag instead of an exception object. Most implementations should
     * override [close] instead of this method.
     *
     * @param completedSuccessfully True if the stream processed successfully
     */
    suspend fun teardown(completedSuccessfully: Boolean) {
        if (completedSuccessfully) {
            close(true, null)
        } else {
            close(true, StreamProcessingFailed(Exception("One or more streams did not complete.")))
        }
    }
}
