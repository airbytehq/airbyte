/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

/** DataChannelFormat defines the wire format for Records and state messages sent over the wire. */
enum class DataChannelFormat {
    JSONL,
    PROTOBUF,
}
