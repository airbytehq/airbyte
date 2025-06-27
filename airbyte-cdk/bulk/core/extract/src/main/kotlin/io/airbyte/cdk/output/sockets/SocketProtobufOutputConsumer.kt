/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import com.fasterxml.jackson.databind.SequenceWriter
import com.google.protobuf.CodedOutputStream
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.time.Clock

// Emits Airbyte protobuf messages to a socket data channel.
// TODO: optimize record message serialization by creating the bytes surrounding a record data once
class SocketProtobufOutputConsumer(
    private val dataChannel: SocketDataChannel,
    clock: Clock,
    val bufferByteSizeThresholdForFlush: Int,
) : OutputConsumer(clock) {
    private val log = KotlinLogging.logger {}
    private val buffer = ByteArrayOutputStream()
    private val c = CodedOutputStream.newInstance(buffer)

    override fun accept(airbyteMessage: io.airbyte.protocol.models.v0.AirbyteMessage) {
        // This method effectively println's its JSON-serialized argument.
        // Using println is not particularly efficient, however.
        // To improve performance, this method accumulates RECORD messages into a buffer
        // before writing them to standard output in a batch.
        if (airbyteMessage.type == io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD) {
            // RECORD messages undergo a different serialization scheme.
            // accept(airbyteMessage.record)
            // no-op
        } else {
            synchronized(this) {
                val b = ByteArrayOutputStream()
                val sequenceWriter: SequenceWriter = Jsons.writer().writeValues(b)
                sequenceWriter.write(airbyteMessage)
                sequenceWriter.flush()

                val pm =
                    AirbyteMessageProtobuf.newBuilder()
                        .setAirbyteProtocolMessage(String(b.toByteArray()))
                        .build()
                pm.writeDelimitedTo(buffer)
                log.info { "AirbyteMessage sent over SOCKET: ${String(b.toByteArray())}" }
                withLockFlush()
            }
        }
    }
    fun accept(airbyteProtoMessage: AirbyteMessageProtobuf) {
        synchronized(this) {
//            airbyteProtoMessage.writeDelimitedTo(buffer)
            c.writeUInt32NoTag(airbyteProtoMessage.serializedSize)
            airbyteProtoMessage.writeTo(c)
//            c.flush()
            if (buffer.size() >= bufferByteSizeThresholdForFlush) {
                withLockFlush()
            }
        }
    }

    private fun withLockFlush() {
        if (buffer.size() > 0) {
            buffer.writeTo(dataChannel.outputStream)
            buffer.reset()
        }
    }

    override fun close() {
        synchronized(this) {
            c.flush()
            // Flush any remaining buffer contents to stdout before closing.
            withLockFlush()
        }
    }
}
