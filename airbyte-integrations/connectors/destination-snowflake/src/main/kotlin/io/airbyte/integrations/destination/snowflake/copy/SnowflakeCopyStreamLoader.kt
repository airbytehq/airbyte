/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.cdk.load.write.StreamLoader

/** Teardown runs after the pipeline has drained all batch uploads, including for empty streams. */
internal class SnowflakeCopyStreamLoader(
    private val delegate: StreamLoader,
    private val copy: SnowflakeS3Copy,
) : StreamLoader by delegate {
    override suspend fun teardown(completedSuccessfully: Boolean) {
        delegate.teardown(completedSuccessfully)
        if (completedSuccessfully) copy.complete(stream)
    }
}
