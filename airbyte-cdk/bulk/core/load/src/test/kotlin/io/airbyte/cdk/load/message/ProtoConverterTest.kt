package io.airbyte.cdk.load.message

import com.google.protobuf.ByteString
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.protocol.AirbyteCommons
import io.airbyte.protocol.AirbyteRecord.AirbyteRecordMessage
import io.airbyte.protocol.AirbyteTrace
import io.airbyte.protocol.Protocol
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.mockk.every
import io.mockk.mockk
import java.io.File
import java.nio.file.Files
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class ProtoConverterTest {
    @Disabled("This is just to make test data")
    @Test
    fun jsonToProto() {
        val jsonlFile = javaClass.getResource("/test-data-1-stream-100k-rows.json")
            ?: error("test-data-1-stream-100k-rows.jsonl not found")
        val outFile = File("test-data-1-stream-100k.jsonl.out")
        val outputStream = Files.newOutputStream(outFile.toPath())
        // read 1 line at a time
        val stream = mockk<DestinationStream>()
        every { stream.descriptor } returns DestinationStream.Descriptor(
            "johnny",
            "users"
        )
        every { stream.schema } returns ObjectTypeWithoutSchema
        val factory = DestinationMessageFactory(
            DestinationCatalog(streams = listOf(stream)), false)
        outputStream.use { outputStream ->
            jsonlFile.openStream().bufferedReader().use { reader ->
                reader.lineSequence().forEach { line ->
                    val abMessage = line.deserializeToClass(AirbyteMessage::class.java)
                    val dMessage = factory.fromAirbyteMessage(abMessage, line)
                    val pMessage = when (dMessage) {
                        is DestinationRecord -> {
                            Protocol.AirbyteMessage.newBuilder()
                                .setType(Protocol.AirbyteMessageType.RECORD)
                                .setRecord(
                                    AirbyteRecordMessage.newBuilder()
                                        .setStream(dMessage.stream.descriptor.name)
                                        .setNamespace(dMessage.stream.descriptor.namespace)
                                        .setData(ByteString.copyFrom(dMessage.data.serializeToJsonBytes()))
                                        .setEmittedAt(dMessage.emittedAtMs)
                                        .build()
                                )
                                .build()
                        }

                        is DestinationRecordStreamComplete -> {
                            Protocol.AirbyteMessage.newBuilder()
                                .setType(Protocol.AirbyteMessageType.TRACE_MESSAGE)
                                .setTrace(
                                    AirbyteTrace.AirbyteTraceMessage.newBuilder()
                                        .setType(AirbyteTrace.AirbyteTraceMessageType.STREAM_STATUS)
                                        .setStreamStatus(
                                            AirbyteTrace.AirbyteStreamStatusTraceMessage.newBuilder()
                                                .setStatus(AirbyteTrace.AirbyteStreamStatus.COMPLETE)
                                                .setStreamDescriptor(
                                                    AirbyteCommons.AirbyteStreamDescriptor.newBuilder()
                                                        .setName(dMessage.stream.descriptor.name)
                                                        .setNamespace(dMessage.stream.descriptor.namespace)
                                                        .build()
                                                )
                                        )
                                        .setEmittedAt(dMessage.emittedAtMs)
                                        .build()
                                )
                                .build()
                        }

                        else -> null
                    }
                    pMessage?.writeDelimitedTo(outputStream)
                }
            }
        }
    }

    @Disabled("This is just to test that the test data worked")
    @Test
    fun readProto() {
        val protoFile = javaClass.getResource("/test-data-1-stream-100k-rows.proto")
            ?: error("test-data-1-stream-100k-rows.jsonl.out not found")
        val parser = Protocol.AirbyteMessage.parser()
        val inputStream = protoFile.openStream()
        while (true) {
            val message = parser.parseDelimitedFrom(inputStream) ?: break
            println(message)
        }
    }
}
