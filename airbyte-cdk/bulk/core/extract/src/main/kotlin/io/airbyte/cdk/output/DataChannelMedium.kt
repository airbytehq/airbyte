/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

/**
 * DataChannelMedium defines the medium over which Records and state messages are sent. It can be
 * either STDIO (standard input/output) or SOCKET (unix domain sockets).
 */
enum class DataChannelMedium {
    STDIO,
    SOCKET,
}
