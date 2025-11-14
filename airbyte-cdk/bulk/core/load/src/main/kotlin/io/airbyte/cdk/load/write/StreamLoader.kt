/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed

/**
 * Implementor interface. A stream event handler.
 *
 * [start] is called once before any records are processed.
 *
 * [close] is called once after all records have been processed, regardless of success or failure,
 * but only if [start] returned successfully. If any exception was thrown during processing, it is
 * passed as an argument to [close]. `hadNonzeroRecords` is only used by legacy typing and deduping
 * and `streamFailure` is only used as a boolean flag - it's internal exception is not read.
 *
 * [teardown] provides a simpler API for calling [close], which itself is used by existing
 * destinations to perform finalization and clean up of temporary tables, etc.
 */
interface StreamLoader {
    val stream: DestinationStream

    suspend fun start() {}

    suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed? = null) {}

    suspend fun teardown(completedSuccessfully: Boolean) {
        if (completedSuccessfully) {
            close(true, null)
        } else {
            close(true, StreamProcessingFailed(Exception("One or more streams did not complete.")))
        }
    }
}
