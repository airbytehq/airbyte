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
 * [teardown] is called once after all records have been processed, regardless of success or
 * failure, but only if [start] returned successfully.
 */
interface StreamLoader {
    val stream: DestinationStream

    suspend fun start() {}

    suspend fun teardown(completedSuccessfully: Boolean) {}
}
