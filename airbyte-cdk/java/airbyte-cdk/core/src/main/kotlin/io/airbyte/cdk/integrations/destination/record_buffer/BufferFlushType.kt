/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

enum class BufferFlushType {
    FLUSH_ALL,
    FLUSH_SINGLE_STREAM
}
