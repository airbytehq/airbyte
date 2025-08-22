/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import com.fasterxml.jackson.databind.SequenceWriter
import com.google.protobuf.CodedOutputStream
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
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
    val additionalProperties: Map<String, String>,
) : OutputConsumer(clock) {
    private val log = KotlinLogging.logger {}
    private val buffer = ByteArrayOutputStream()
    private val cos = CodedOutputStream.newInstance(buffer)

    override fun accept(airbyteMessage: AirbyteMessage) {
        // This method effectively println's its JSON-serialized argument.
        // Using println is not particularly efficient, however.
        // To improve performance, this method accumulates RECORD messages into a buffer
        // before writing them to standard output in a batch.
        if (airbyteMessage.type == AirbyteMessage.Type.RECORD) {
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
                withLockFlush()
            }
        }
    }
    fun accept(airbyteProtoMessage: AirbyteMessageProtobuf) {
        synchronized(this) {
            // This is the equivalent of writeDelimitedTo,
            // Writing the size of the message first.
            cos.writeUInt32NoTag(airbyteProtoMessage.serializedSize)
            airbyteProtoMessage.writeTo(cos)
            if (buffer.size() >= bufferByteSizeThresholdForFlush) {
                withLockFlush()
            }
        }
    }

    private fun withLockFlush() {
        cos.flush()
        if (buffer.size() > 0) {
            buffer.writeTo(dataChannel.outputStream)
            buffer.reset()
        }
    }

    override fun close() {
        synchronized(this) {
            // Flush any remaining buffer contents to stdout before closing.
            withLockFlush()
        }
    }
}
