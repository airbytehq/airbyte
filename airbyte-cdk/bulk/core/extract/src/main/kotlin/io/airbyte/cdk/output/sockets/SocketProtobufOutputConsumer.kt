package io.airbyte.cdk.output.sockets

import com.fasterxml.jackson.databind.SequenceWriter
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.time.Clock

class SocketProtobufOutputConsumer(
    private val dataChannel: SocketDataChannel,
    clock: Clock,
    val bufferByteSizeThresholdForFlush: Int,
): OutputConsumer(clock)
{
    private val log = KotlinLogging.logger {}
    private val buffer = ByteArrayOutputStream()

    override fun accept(airbyteMessage: io.airbyte.protocol.models.v0.AirbyteMessage) {
        // This method effectively println's its JSON-serialized argument.
        // Using println is not particularly efficient, however.
        // To improve performance, this method accumulates RECORD messages into a buffer
        // before writing them to standard output in a batch.
        if (airbyteMessage.type == io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD) {
            // RECORD messages undergo a different serialization scheme.
            //accept(airbyteMessage.record)
            //no-op
        } else {
            synchronized(this) {
                val b = ByteArrayOutputStream()
                val sequenceWriter: SequenceWriter = Jsons.writer().writeValues(b)
                sequenceWriter.write(airbyteMessage)
                sequenceWriter.flush()

                val pm = AirbyteMessageProtobuf.newBuilder()
                    .setAirbyteProtocolMessage(String(b.toByteArray()))
                    .build()
                pm.writeDelimitedTo(buffer)

//                // Write a newline character to the buffer if it's not empty.
//                withLockMaybeWriteNewline()
//                // Non-RECORD AirbyteMessage instances are serialized and written to the buffer
//                // using standard jackson object mapping facilities.
//                sequenceWriter.write(airbyteMessage)
//                sequenceWriter.flush()
//                // Such messages don't linger in the buffer, they are flushed to stdout immediately,
//                // along with whatever might have already been lingering inside.
//                // This prints a newline after the message.
                log.info { "AirbyteMessage sent over SOCKET: ${String(b.toByteArray())}" }
                withLockFlush()
            }
        }
    }
    fun accept(airbyteProtoMessage: AirbyteMessageProtobuf) {
        synchronized(this) {
            airbyteProtoMessage.writeDelimitedTo(buffer)
            if (buffer.size() >= bufferByteSizeThresholdForFlush) {
                withLockFlush()
            }

        }
    }

    private fun withLockFlush() {
        if (buffer.size() > 0) {
            buffer.writeTo(dataChannel.outputStream)
//            socket.outputStream?.write(System.lineSeparator().toByteArray())
//            stdout.println(buffer.toString(Charsets.UTF_8))
//            stdout.flush()
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
