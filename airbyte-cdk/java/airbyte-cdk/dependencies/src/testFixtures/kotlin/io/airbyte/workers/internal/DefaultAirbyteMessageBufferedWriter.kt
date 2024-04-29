/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.AirbyteMessage
import java.io.BufferedWriter
import java.io.IOException

class DefaultAirbyteMessageBufferedWriter(protected val writer: BufferedWriter) :
    AirbyteMessageBufferedWriter {
    @Throws(IOException::class)
    override fun write(message: AirbyteMessage) {
        writer.write(Jsons.serialize(message))
        writer.newLine()
    }

    @Throws(IOException::class)
    override fun flush() {
        writer.flush()
    }

    @Throws(IOException::class)
    override fun close() {
        writer.close()
    }
}
