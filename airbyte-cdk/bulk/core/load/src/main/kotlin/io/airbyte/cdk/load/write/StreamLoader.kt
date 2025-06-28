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
 * passed as an argument to [close].
 */
interface StreamLoader {
    val stream: DestinationStream

    suspend fun start() {}

    suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed? = null) {}
}
