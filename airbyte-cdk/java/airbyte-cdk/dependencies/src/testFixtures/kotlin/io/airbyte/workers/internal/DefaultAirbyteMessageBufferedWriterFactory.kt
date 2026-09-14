/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import java.io.BufferedWriter

class DefaultAirbyteMessageBufferedWriterFactory : AirbyteMessageBufferedWriterFactory {
    override fun createWriter(writer: BufferedWriter): AirbyteMessageBufferedWriter {
        return DefaultAirbyteMessageBufferedWriter(writer)
    }
}
