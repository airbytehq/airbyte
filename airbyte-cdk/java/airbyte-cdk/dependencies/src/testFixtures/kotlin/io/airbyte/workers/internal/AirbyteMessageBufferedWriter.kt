/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import io.airbyte.protocol.models.AirbyteMessage
import java.io.IOException

interface AirbyteMessageBufferedWriter {
    @Throws(IOException::class) fun write(message: AirbyteMessage)

    @Throws(IOException::class) fun flush()

    @Throws(IOException::class) fun close()
}
