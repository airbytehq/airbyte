/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.google.protobuf.Any
import com.google.protobuf.ByteString
import com.google.protobuf.DescriptorProtos
import com.google.protobuf.Descriptors
import com.google.protobuf.DynamicMessage
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.util.FastUUIDGenerator
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.protocol.AirbyteCommons
import io.airbyte.protocol.AirbyteRecord
import io.airbyte.protocol.AirbyteRecord.AirbyteRecordMessage
import io.airbyte.protocol.AirbyteTrace
import io.airbyte.protocol.Protocol
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.micronaut.core.execution.ExecutionFlow.async
import io.mockk.every
import io.mockk.mockk
import java.io.File
import java.io.OutputStream
import java.nio.file.Files
import java.security.SecureRandom
import java.util.*
import kotlin.time.measureTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.joinAll
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withContext
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class ProtoConverterTest {
    @Disabled("This is just to make test data")
    @Test
    fun jsonToProto() {
        val jsonlFile =
            javaClass.getResource("/test-data-1-stream-100k-rows.json")
                ?: error("test-data-1-stream-100k-rows.jsonl not found")
        val outFile = File("test-data-1-stream-100k.jsonl.out")
        val outputStream = Files.newOutputStream(outFile.toPath())
        // read 1 line at a time
        val stream = mockk<DestinationStream>()
        every { stream.descriptor } returns DestinationStream.Descriptor("johnny", "users")
        every { stream.schema } returns ObjectTypeWithoutSchema
        val factory = DestinationMessageFactory(DestinationCatalog(streams = listOf(stream)), false)
        outputStream.use { outputStream ->
            jsonlFile.openStream().bufferedReader().use { reader ->
                reader.lineSequence().forEach { line ->
                    val abMessage = line.deserializeToClass(AirbyteMessage::class.java)
                    val dMessage = factory.fromAirbyteMessage(abMessage, line)
                    val pMessage =
                        when (dMessage) {
                            is DestinationRecord -> {
                                Protocol.AirbyteMessage.newBuilder()
                                    .setType(Protocol.AirbyteMessageType.RECORD)
                                    .setRecord(
                                        AirbyteRecordMessage.newBuilder()
                                            .setStream(dMessage.stream.descriptor.name)
                                            .setNamespace(dMessage.stream.descriptor.namespace)
//                                            .setData(
//                                                ByteString.copyFrom(
//                                                    dMessage.data.serializeToJsonBytes()
//                                                )
//                                            )
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
                                            .setType(
                                                AirbyteTrace.AirbyteTraceMessageType.STREAM_STATUS
                                            )
                                            .setStreamStatus(
                                                AirbyteTrace.AirbyteStreamStatusTraceMessage
                                                    .newBuilder()
                                                    .setStatus(
                                                        AirbyteTrace.AirbyteStreamStatus.COMPLETE
                                                    )
                                                    .setStreamDescriptor(
                                                        AirbyteCommons.AirbyteStreamDescriptor
                                                            .newBuilder()
                                                            .setName(
                                                                dMessage.stream.descriptor.name
                                                            )
                                                            .setNamespace(
                                                                dMessage.stream.descriptor.namespace
                                                            )
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
        val protoFile =
            javaClass.getResource("/test-data-1-stream-100k-rows.proto")
                ?: error("test-data-1-stream-100k-rows.jsonl.out not found")
        val parser = Protocol.AirbyteMessage.parser()
        val inputStream = protoFile.openStream()
        while (true) {
            val message = parser.parseDelimitedFrom(inputStream) ?: break
            println(message)
        }
    }
    enum class DataType {
        DATETIME, LONG, STRING, INT, FLOAT, BOOLEAN, BINARY
    }

//    @Disabled("This is just a temporary performance test")
//    @Test
//    fun performanceTest() {
//        val timestamp: String = "2023-10-01T00:00:00Z"
//        val id: Long = 123451L
//        val name: String = "John Doe"
//        val price: Double = 123.45
//        val interactions: Int = 100
//        val isActive: Boolean = true
//        val rawData: ByteString = ByteString.copyFromUtf8(
//            """{"timestamp":"$timestamp","id":$id,"name":"$name","price":$price,"isActive":$isActive}"""
//        )
//        val types = listOf(
//            DataType.DATETIME,
//            DataType.LONG,
//            DataType.STRING,
//            DataType.FLOAT,
//            DataType.INT,
//            DataType.BOOLEAN,
//            DataType.BINARY
//        )
//
//        val devNullOutputStream = object: OutputStream() {
//            override fun write(b: Int) {
//                // do nothing
//            }
//        }
//
//        val fileDescriptorProto = DescriptorProtos.FileDescriptorProto.newBuilder()
//            .setName("dynamic.proto")
//            .setSyntax("proto3")
//            .setPackage("io.airbyte.protocol.dynamic")
//        val messageBuilder = DescriptorProtos.DescriptorProto.newBuilder()
//            .setName("ClientSchema")
//
//        // Add all the schema fields
//        messageBuilder.addField(
//            DescriptorProtos.FieldDescriptorProto.newBuilder()
//                .setName("timestamp")
//                .setNumber(1)
//                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING)
//                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
//        )
//        messageBuilder.addField(
//            DescriptorProtos.FieldDescriptorProto.newBuilder()
//                .setName("id")
//                .setNumber(2)
//                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_UINT64)
//                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
//        )
//        messageBuilder.addField(
//            DescriptorProtos.FieldDescriptorProto.newBuilder()
//                .setName("name")
//                .setNumber(3)
//                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_STRING)
//                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
//        )
//        messageBuilder.addField(
//            DescriptorProtos.FieldDescriptorProto.newBuilder()
//                .setName("price")
//                .setNumber(4)
//                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_DOUBLE)
//                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
//        )
//        messageBuilder.addField(
//            DescriptorProtos.FieldDescriptorProto.newBuilder()
//                .setName("interactions")
//                .setNumber(5)
//                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_INT32)
//                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
//        )
//        messageBuilder.addField(
//            DescriptorProtos.FieldDescriptorProto.newBuilder()
//                .setName("is_active")
//                .setNumber(6)
//                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_BOOL)
//                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
//        )
//        messageBuilder.addField(
//            DescriptorProtos.FieldDescriptorProto.newBuilder()
//                .setName("raw_data")
//                .setNumber(7)
//                .setType(DescriptorProtos.FieldDescriptorProto.Type.TYPE_BYTES)
//                .setLabel(DescriptorProtos.FieldDescriptorProto.Label.LABEL_OPTIONAL)
//        )
//        fileDescriptorProto.addMessageType(messageBuilder)
//        val fileDescriptor = Descriptors.FileDescriptor.buildFrom(fileDescriptorProto.build(), arrayOf())
//        val messageDescriptor = fileDescriptor.findMessageTypeByName("ClientSchema")
//
//        val repetitions = 100_000_000
//        val durationAnon = measureTime {
//            val builder = AirbyteRecordMessage.newBuilder()
//                .setStream("test_stream")
//                .setNamespace("test_namespace")
//                .setEmittedAt(System.currentTimeMillis())
//            val b = AirbyteRecord.AirbyteValue.newBuilder()
//            repeat(repetitions) {
//                types.forEach { t ->
//                    when (t) {
//                        DataType.DATETIME -> builder.addData(b.setStringValue(timestamp).build())
//                        DataType.LONG -> builder.addData(b.setLongValue(id).build())
//                        DataType.STRING -> builder.addData(b.setStringValue(name).build())
//                        DataType.FLOAT -> builder.addData(b.setDoubleValue(price).build())
//                        DataType.INT -> builder.addData(b.setIntValue(interactions).build())
//                        DataType.BOOLEAN -> builder.addData(b.setBooleanValue(isActive).build())
//                        DataType.BINARY -> builder.addData(b.setBytesValue(rawData).build())
//                    }
//                }
//                builder.build().writeDelimitedTo(devNullOutputStream)
//                builder.clearData()
//            }
//        }
//
//        val durationAnon2 = measureTime {
//            val builder = AirbyteRecordMessage.newBuilder()
//                .setStream("test_stream")
//                .setNamespace("test_namespace")
//                .setEmittedAt(System.currentTimeMillis())
//            // prepopulate the data list
//            repeat (types.size) {
//                builder.addData(
//                    AirbyteRecord.AirbyteValue.newBuilder()
//                        .setIntValue(0)
//                        .build()
//                )
//            }
//            val b = AirbyteRecord.AirbyteValue.newBuilder()
//            repeat(repetitions) {
//                types.forEachIndexed { i, t ->
//                    when (t) {
//                        DataType.DATETIME -> builder.setData(i, b.setStringValue(timestamp).build())
//                        DataType.LONG -> builder.setData(i, b.setLongValue(id).build())
//                        DataType.STRING -> builder.setData(i, b.setStringValue(name).build())
//                        DataType.FLOAT -> builder.setData(i, b.setDoubleValue(price).build())
//                        DataType.INT -> builder.setData(i, b.setIntValue(interactions).build())
//                        DataType.BOOLEAN -> builder.setData(i, b.setBooleanValue(isActive).build())
//                        DataType.BINARY -> builder.setData(i, b.setBytesValue(rawData).build())
//                    }
//                }
//                builder.build().writeDelimitedTo(devNullOutputStream)
//            }
//        }
//
//        val durationFixed = measureTime {
//            val builder = AirbyteRecord.AirbyteRecordMessageHacked.newBuilder()
//                .setStream("test_stream")
//                .setNamespace("test_namespace")
//                .setEmittedAt(System.currentTimeMillis())
//            val b = FakeGeneratedMessage.newBuilder()
//            repeat(repetitions) {
//                types.forEach { t ->
//                    when (t) {
//                        DataType.DATETIME -> b.setTimestamp(timestamp)
//                        DataType.LONG -> b.setId(id)
//                        DataType.STRING -> b.setName(name)
//                        DataType.FLOAT -> b.setPrice(price)
//                        DataType.INT -> b.setInteractions(interactions)
//                        DataType.BOOLEAN -> b.setIsActive(isActive)
//                        DataType.BINARY -> b.setRawData(rawData)
//                    }
//                }
//                builder.setData(b.build())
//                builder.build().writeDelimitedTo(devNullOutputStream)
//            }
//        }
//
//        val fds = Array(types.size) { i -> messageDescriptor.findFieldByNumber(i + 1) }
//        val durationDynamic = measureTime {
//            val builder = AirbyteRecord.AirbyteRecordMessageAny.newBuilder()
//                .setStream("test_stream")
//                .setNamespace("test_namespace")
//                .setEmittedAt(System.currentTimeMillis())
//            val db = DynamicMessage.newBuilder(messageDescriptor)
//            repeat(repetitions) {
//                types.forEachIndexed { i, t ->
//                    when (t) {
//                        DataType.DATETIME -> db.setField(fds[i], timestamp)
//                        DataType.LONG -> db.setField(fds[i], id)
//                        DataType.STRING -> db.setField(fds[i], name)
//                        DataType.FLOAT -> db.setField(fds[i], price)
//                        DataType.INT -> db.setField(fds[i], interactions)
//                        DataType.BOOLEAN -> db.setField(fds[i], isActive)
//                        DataType.BINARY -> db.setField(fds[i], rawData)
//                    }
//                }
//                builder.setData(Any.pack(db.build()))
//                builder.build().writeDelimitedTo(devNullOutputStream)
//            }
//        }
//
//        println("Anon: $durationAnon")
//        println("Anon2: $durationAnon2")
//        println("Fixed: $durationFixed")
//        println("Dynamic: $durationDynamic")
//    }

    //@Disabled("Just to test fast-uuid performance")
    @Test
    fun fastUUIDPerformance() = runBlocking {
        val repetitions = 1_000_000
        val threads = 4

        val javaUUID = measureTime {
            withContext(Dispatchers.IO) {
                (0 until threads).map {
                    async {
                        repeat(repetitions) {
                            UUID.randomUUID().toString()
                        }
                    }
                }.joinAll()
            }
        }

        val catalog = DestinationCatalog(
            streams = listOf(
                DestinationStream(
                    descriptor = DestinationStream.Descriptor("johnny", "users"),
                    schema = ObjectTypeWithoutSchema,
                    syncId = 1234L,
                    generationId = 1,
                    minimumGenerationId = 1,
                    importType = Overwrite,
                )
            )
        )
        val gen = FastUUIDGenerator()
        val fastUUID = measureTime {
            withContext(Dispatchers.IO) {
                (0 until threads).map {
                    repeat(repetitions) {
                        gen.insecureUUID().toString()
                    }
                }
            }
        }

        println("Java UUID: $javaUUID")
        println("Fast UUID: $fastUUID")
    }

    @Test
    fun testUUIDFormat() {
        println(FastUUIDGenerator().insecureUUID().toString())
    }
}
