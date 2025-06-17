/*
 * Copyright (c) 2025 Airbyte, Inc.
 */
package io.airbyte.cdk.load.file.object_storage

import com.google.protobuf.kotlin.toByteString
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import io.mockk.every
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.unmockkAll
import java.io.ByteArrayOutputStream
import java.util.UUID
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ProtoToJsonFormattingTest {

    private val uuid: UUID = UUID.fromString("11111111-1111-1111-1111-111111111111")
    private val emittedAtMs = 1_724_438_400_000L
    private val syncId = 42L
    private val generationId = 314L

    private lateinit var stream: DestinationStream
    private var protoSource: DestinationRecordProtobufSource? = null
    private lateinit var record: DestinationRecordRaw
    private lateinit var fieldAccessors: Array<AirbyteValueProxy.FieldAccessor>

    @BeforeEach
    fun setUp() {
        fieldAccessors =
            arrayOf(
                field("bool_col", BooleanType, 0),
                field("int_col", IntegerType, 1),
                field("num_col", NumberType, 2),
                field("string_col", StringType, 3),
                field("date_col", DateType, 4),
                field("time_tz_col", TimeTypeWithTimezone, 5),
                field("time_no_tz_col", TimeTypeWithoutTimezone, 6),
                field("ts_tz_col", TimestampTypeWithTimezone, 7),
                field("ts_no_tz_col", TimestampTypeWithoutTimezone, 8),
                field("array_col", ArrayType(FieldType(StringType, false)), 9),
                field("obj_col", ObjectType(linkedMapOf("k" to FieldType(StringType, false))), 10),
                field("union_col", UnionType(setOf(StringType), false), 11),
                field("unknown_col", UnknownType(Jsons.emptyObject()), 12),
            )

        val protoValues =
            listOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBoolean(true).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setInteger(123).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setNumber(12.34).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("hello").build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setDate("2025-06-17")
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setTimeWithTimezone("23:59:59+02")
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setTimeWithoutTimezone("23:59:59")
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setTimestampWithTimezone("2025-06-17T23:59:59+02")
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setTimestampWithoutTimezone("2025-06-17T23:59:59")
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setJson("""["a","b"]""".toByteArray().toByteString())
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setJson("""{"k":"v"}""".toByteArray().toByteString())
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setJson("""{"u":1}""".toByteArray().toByteString())
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setIsNull(true)
                    .build(), // unknown_col
            )

        val metaProto =
            AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMeta.newBuilder()
                .addChanges(
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange.newBuilder()
                        .setField("x")
                        .setChange(
                            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED
                        )
                        .setReason(
                            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                                .DESTINATION_SERIALIZATION_ERROR
                        ),
                )
                .addChanges(
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange.newBuilder()
                        .setField("y")
                        .setChange(
                            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED
                        )
                        .setReason(
                            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                                .SOURCE_SERIALIZATION_ERROR
                        ),
                )
                .addChanges(
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange.newBuilder()
                        .setField("z")
                        .setChange(
                            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.TRUNCATED
                        )
                        .setReason(
                            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                                .SOURCE_RECORD_SIZE_LIMITATION
                        ),
                )
                .build()

        val recordProto =
            AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                .setStreamName("dummy")
                .setEmittedAtMs(emittedAtMs)
                .addAllData(protoValues)
                .setMeta(metaProto)
                .build()

        val airbyteMessageProto =
            AirbyteMessage.AirbyteMessageProtobuf.newBuilder().setRecord(recordProto).build()

        protoSource = DestinationRecordProtobufSource(airbyteMessageProto)

        stream = mockk {
            every { this@mockk.airbyteValueProxyFieldAccessors } returns fieldAccessors
            every { this@mockk.syncId } returns this@ProtoToJsonFormattingTest.syncId
            every { this@mockk.generationId } returns this@ProtoToJsonFormattingTest.generationId
        }

        record =
            mockk(relaxed = true) {
                every { this@mockk.airbyteRawId } returns uuid
                every { this@mockk.rawData } returns protoSource!!
                every { this@mockk.stream } returns this@ProtoToJsonFormattingTest.stream
            }
    }

    @AfterEach fun tearDown() = unmockkAll()

    private fun field(name: String, type: AirbyteType, idx: Int): AirbyteValueProxy.FieldAccessor =
        mockk {
            every { this@mockk.name } returns name
            every { this@mockk.type } returns type
            try {
                every { this@mockk.index } returns idx
            } catch (_: Exception) {}
        }

    @Test
    fun `formatter writes ND-JSON with trailing newline`() {
        val out = ByteArrayOutputStream()
        val formatter = ProtoToJsonFormatter(stream, out, rootLevelFlattening = true)

        formatter.accept(record)
        formatter.flush()

        val lines = out.toString(Charsets.UTF_8).split('\n')
        assertEquals(2, lines.size) // record + final newline

        assertEquals(
            "{\"_airbyte_raw_id\":\"11111111-1111-1111-1111-111111111111\",\"_airbyte_extracted_at\":1724438400000,\"_airbyte_meta\":{\"sync_id\":42,\"changes\":[{\"field\":\"x\",\"change\":\"NULLED\",\"reason\":\"DESTINATION_SERIALIZATION_ERROR\"},{\"field\":\"y\",\"change\":\"NULLED\",\"reason\":\"SOURCE_SERIALIZATION_ERROR\"},{\"field\":\"z\",\"change\":\"TRUNCATED\",\"reason\":\"SOURCE_RECORD_SIZE_LIMITATION\"}]},\"_airbyte_generation_id\":314,\"bool_col\":true,\"int_col\":123,\"num_col\":12.34,\"string_col\":\"hello\",\"date_col\":\"2025-06-17\",\"time_tz_col\":\"23:59:59+02\",\"time_no_tz_col\":\"23:59:59\",\"ts_tz_col\":\"2025-06-17T23:59:59+02\",\"ts_no_tz_col\":\"2025-06-17T23:59:59\",\"array_col\":[\"a\",\"b\"],\"obj_col\":{\"k\":\"v\"},\"union_col\":{\"u\":1},\"unknown_col\":null}",
            lines[0],
        )
        assertEquals("", lines[1])
    }

    @Test
    fun `formatter writes ND-JSON with trailing newline non-flatten`() {
        val out = ByteArrayOutputStream()
        val formatter = ProtoToJsonFormatter(stream, out, rootLevelFlattening = false)

        formatter.accept(record)
        formatter.flush()

        val lines = out.toString(Charsets.UTF_8).split('\n')
        assertEquals(2, lines.size) // record + final newline

        assertEquals(
            "{\"_airbyte_raw_id\":\"11111111-1111-1111-1111-111111111111\",\"_airbyte_extracted_at\":1724438400000,\"_airbyte_meta\":{\"sync_id\":42,\"changes\":[{\"field\":\"x\",\"change\":\"NULLED\",\"reason\":\"DESTINATION_SERIALIZATION_ERROR\"},{\"field\":\"y\",\"change\":\"NULLED\",\"reason\":\"SOURCE_SERIALIZATION_ERROR\"},{\"field\":\"z\",\"change\":\"TRUNCATED\",\"reason\":\"SOURCE_RECORD_SIZE_LIMITATION\"}]},\"_airbyte_generation_id\":314,\"_airbyte_data\":{\"bool_col\":true,\"int_col\":123,\"num_col\":12.34,\"string_col\":\"hello\",\"date_col\":\"2025-06-17\",\"time_tz_col\":\"23:59:59+02\",\"time_no_tz_col\":\"23:59:59\",\"ts_tz_col\":\"2025-06-17T23:59:59+02\",\"ts_no_tz_col\":\"2025-06-17T23:59:59\",\"array_col\":[\"a\",\"b\"],\"obj_col\":{\"k\":\"v\"},\"union_col\":{\"u\":1},\"unknown_col\":null}}",
            lines[0],
        )
        assertEquals("", lines[1])
    }

    @Test
    fun `formatter throws on non-protobuf record`() {
        val nonProtoRecord =
            mockk<DestinationRecordRaw> {
                every { rawData } returns mockk<DestinationRecordSource>(relaxed = true)
            }
        val formatter = ProtoToJsonFormatter(stream, ByteArrayOutputStream(), false)

        val ex = assertThrows(RuntimeException::class.java) { formatter.accept(nonProtoRecord) }
        assertTrue(ex.message!!.contains("only supports conversion"))
    }
}
