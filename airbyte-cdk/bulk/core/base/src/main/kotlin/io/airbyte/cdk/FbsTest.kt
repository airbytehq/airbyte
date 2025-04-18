package io.airbyte.cdk

import com.google.flatbuffers.FlatBufferBuilder
import io.airbyte.protocol.AirbyteBooleanValue
import io.airbyte.protocol.AirbyteLongValue
import io.airbyte.protocol.AirbyteRecordMessage
import io.airbyte.protocol.AirbyteStringValue
import io.airbyte.protocol.AirbyteValue
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.OutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

fun main(args: Array<String>) {
    val outputStream = ByteArrayOutputStream()
    val total = 100000
    val messages = generateFbsMessages(total)

    val writeStartTime = System.currentTimeMillis()
    writeFbsToOutput(outputStream = outputStream, messages = messages)
    val writeStopTime = System.currentTimeMillis()
    println()
    println("Total write time: ${writeStopTime - writeStartTime} ms")

    val inputStream = ByteArrayInputStream(outputStream.toByteArray())
    val readStartTime = System.currentTimeMillis()
    val count = readFbsFromInput(inputStream)
    val readStopTime = System.currentTimeMillis()
    println("Total read time = ${readStopTime - readStartTime} ms")

    println()
    if (count == total) {
        println("Read all messages.")
    } else {
        println("Did not read all messages: $count")
    }
}

fun testing() {
    val b = FlatBufferBuilder()
    val name = b.createString("foo")
    val namespace = b.createString("bar")
    val data = arrayOf(
        AirbyteBooleanValue.createAirbyteBooleanValue(b, true),
        b.createString("baz").let { offset -> AirbyteStringValue.createAirbyteStringValue(b, offset) },
        AirbyteLongValue.createAirbyteLongValue(b, 10L),
    )
}

fun generateFbsMessages(total: Int): List<AirbyteRecordMessage> {
    val buildStartTime = System.currentTimeMillis()
    val messages =
        (1..total).map { outer ->
            val builder = FlatBufferBuilder()
            val streamNameOffset = builder.createString("stream$outer")
            val streamNamespaceOffset = builder.createString("stream${outer}Namespace")
            val data =
                (1..20).map { inner ->
                    AirbyteLongValue.createAirbyteLongValue(builder, inner.toLong())
                }
            val vector = AirbyteRecordMessage.createDataVector(builder, data.toIntArray())
            AirbyteRecordMessage.startAirbyteRecordMessage(builder)
            AirbyteRecordMessage.addEmittedAt(builder, System.currentTimeMillis())
            AirbyteRecordMessage.addStreamName(builder, streamNameOffset)
            AirbyteRecordMessage.addStreamNamespace(builder, streamNamespaceOffset)
            AirbyteRecordMessage.addData(builder, vector)
            val endIndex = AirbyteRecordMessage.endAirbyteRecordMessage(builder)
            builder.finish(endIndex)
            AirbyteRecordMessage.getRootAsAirbyteRecordMessage(builder.dataBuffer())
        }

    val buildStopTime = System.currentTimeMillis()
    println("Total build time: ${buildStopTime - buildStartTime} ms")
    return messages
}

fun readFbsFromInput(inputStream: InputStream): Int {
    var count = 0
    while (inputStream.available() > 0) {
        val size = ByteArray(4)
        val bytesRead = inputStream.read(size, 0, 4)
        if (bytesRead == 4) {
            val messageSize = ByteBuffer.wrap(size).order(ByteOrder.LITTLE_ENDIAN).int
            val dataBuffer = ByteArray(messageSize)
            val bufferBytesRead = inputStream.read(dataBuffer)
            val message =
                AirbyteRecordMessage.getRootAsAirbyteRecordMessage(
                    ByteBuffer.wrap(dataBuffer),
                )
            //message.data(AirbyteRecordMessag)
            count++
        }
    }
    return count
}

fun writeFbsToOutput(
    outputStream: OutputStream,
    messages: List<AirbyteRecordMessage>,
) {
    outputStream.use { os ->
        messages.forEach { message ->
            val buffer = message.byteBuffer
            os.write(
                ByteBuffer
                    .allocate(4)
                    .order(ByteOrder.LITTLE_ENDIAN)
                    .putInt(buffer.remaining())
                    .array(),
            )
            os.write(buffer.array(), buffer.position(), buffer.remaining())
        }
    }
}
