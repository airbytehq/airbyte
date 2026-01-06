/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.computeUnknownColumnChanges
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
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import io.mockk.every
import io.mockk.mockk
import io.mockk.unmockkAll
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.util.UUID
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach

abstract class ProtoFixtures(private val addUnknownTypeToSchema: Boolean) {

    val uuid: UUID = UUID.fromString("11111111-1111-1111-1111-111111111111")
    val emittedAtMs = 1_724_438_400_000L
    val syncId = 42L
    val generationId = 314L

    lateinit var stream: DestinationStream
    var protoSource: DestinationRecordProtobufSource? = null
    lateinit var record: DestinationRecordRaw
    lateinit var fieldAccessors: Array<AirbyteValueProxy.FieldAccessor>

    @BeforeEach
    fun setUp() {
        val fields =
            mutableListOf(
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
                field(
                    "union_col",
                    UnionType.of(
                        ObjectType(
                            linkedMapOf(
                                "u" to FieldType(IntegerType, nullable = false),
                            ),
                        ),
                    ),
                    11,
                ),
            )
        if (addUnknownTypeToSchema) {
            fields.add(
                field(
                    "unknown_col",
                    UnknownType(Jsons.emptyObject()),
                    12,
                ),
            )
        }

        fieldAccessors = fields.toTypedArray()

        val encoder = AirbyteValueProtobufEncoder()
        val protoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN),
                encoder.encode(123L, LeafAirbyteSchemaType.INTEGER),
                encoder.encode(12.34, LeafAirbyteSchemaType.NUMBER),
                encoder.encode("hello", LeafAirbyteSchemaType.STRING),
                encoder.encode(LocalDate.parse("2025-06-17"), LeafAirbyteSchemaType.DATE),
                encoder.encode(
                    OffsetTime.parse("23:59:59+02:00"),
                    LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                ),
                encoder.encode(
                    LocalTime.parse("23:59:59"),
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                ),
                encoder.encode(
                    OffsetDateTime.parse("2025-06-17T23:59:59+02:00"),
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                ),
                encoder.encode(
                    LocalDateTime.parse("2025-06-17T23:59:59"),
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                ),
                encoder.encode("""["a","b"]""".toByteArray(), LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"k":"v"}""".toByteArray(), LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"u":1}""".toByteArray(), LeafAirbyteSchemaType.JSONB),
            )

        if (addUnknownTypeToSchema) {
            protoValues.add(
                encoder.encode(null, LeafAirbyteSchemaType.STRING),
            )
        }

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
                .addAllData(protoValues.map { it.build() })
                .setMeta(metaProto)
                .build()

        val airbyteMessageProto =
            AirbyteMessage.AirbyteMessageProtobuf.newBuilder().setRecord(recordProto).build()

        protoSource = DestinationRecordProtobufSource(airbyteMessageProto)

        val dummyType =
            ObjectType(
                linkedMapOf(
                    "bool_col" to FieldType(BooleanType, false),
                    "int_col" to FieldType(IntegerType, false),
                    "num_col" to FieldType(NumberType, false),
                    "string_col" to FieldType(StringType, false),
                    "date_col" to FieldType(DateType, false),
                    "time_tz_col" to FieldType(TimeTypeWithTimezone, false),
                    "time_no_tz_col" to FieldType(TimeTypeWithoutTimezone, false),
                    "ts_tz_col" to FieldType(TimestampTypeWithTimezone, false),
                    "ts_no_tz_col" to FieldType(TimestampTypeWithoutTimezone, false),
                    "array_col" to FieldType(ArrayType(FieldType(StringType, false)), false),
                    "obj_col" to
                        FieldType(
                            ObjectType(linkedMapOf("k" to FieldType(StringType, false))),
                            false,
                        ),
                    "union_col" to
                        FieldType(
                            UnionType.of(
                                ObjectType(
                                    linkedMapOf(
                                        "u" to FieldType(IntegerType, nullable = false),
                                    ),
                                ),
                            ),
                            false,
                        ),
                ),
            )

        if (addUnknownTypeToSchema) {
            dummyType.properties["unknown_col"] = FieldType(UnknownType(Jsons.emptyObject()), false)
        }

        stream = mockk {
            every { this@mockk.airbyteValueProxyFieldAccessors } returns fieldAccessors
            every { this@mockk.syncId } returns this@ProtoFixtures.syncId
            every { this@mockk.generationId } returns this@ProtoFixtures.generationId
            every { this@mockk.schema } returns dummyType
            every { this@mockk.mappedDescriptor } returns DestinationStream.Descriptor("", "dummy")
            every { this@mockk.unknownColumnChanges } returns
                dummyType.computeUnknownColumnChanges()
        }

        record =
            mockk(relaxed = true) {
                every { this@mockk.airbyteRawId } returns uuid
                every { this@mockk.rawData } returns protoSource!!
                every { this@mockk.stream } returns this@ProtoFixtures.stream
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
}
