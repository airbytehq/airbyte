/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream

/**
 * Implementor interface. A stream event handler.
 *
 * [start] is called once before any records are processed.
 *
 * [onStreamFlushed] is called once when all records for this stream have been received (the source
 * sent a StreamComplete message) AND all pending aggregates for this stream have been flushed to
 * the destination. This allows connectors to perform per-stream finalization (e.g., merging a
 * staging branch into the main branch in Iceberg) as soon as the stream's data is fully written,
 * without waiting for the entire sync to complete.
 *
 * [teardown] is called once after all records have been processed, regardless of success or
 * failure, but only if [start] returned successfully.
 */
interface StreamLoader {
    val stream: DestinationStream

    suspend fun start() {}

    /**
     * Called when this stream's data is fully flushed: all records have been received and all
     * pending aggregates for this stream have been written to the destination. Implementations can
     * use this to perform eager per-stream finalization (e.g., promoting staged data to a main
     * branch) before the overall sync completes.
     */
    suspend fun onStreamFlushed() {}

    suspend fun teardown(completedSuccessfully: Boolean) {}
}
