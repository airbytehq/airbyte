/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationStream

/**
 * Used internally by the CDK to keep track of streams while still allowing for partitioning on key.
 */
interface WithStream {
    val stream: DestinationStream.Descriptor
}

/** The default key: partitioned by stream. */
data class StreamKey(override val stream: DestinationStream.Descriptor) : WithStream
