/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.data

import io.airbyte.protocol.models.v0.AirbyteMessage

interface FlowConnector {
    fun close()

    fun pipe(message: AirbyteMessage)
}
