/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream

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
    suspend fun teardown(hadFailure: Boolean = false) {}
}
