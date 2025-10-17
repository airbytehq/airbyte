/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.protobuf.kotlin.toByteString
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.computeUnknownColumnChanges
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
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import io.mockk.every
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.unmockkAll
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.util.UUID
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ProtoToBigQueryStandardInsertRecordFormatterTest {

    private val uuid: UUID = UUID.fromString("11111111-1111-1111-1111-111111111111")
    private val emittedAtMs = 1_724_438_400_000L
    private val syncId = 42L
    private val generationId = 314L

    private lateinit var stream: DestinationStream
    private var protoSource: DestinationRecordProtobufSource? = null
    private lateinit var record: DestinationRecordRaw
    private lateinit var fieldAccessors: Array<AirbyteValueProxy.FieldAccessor>
    private val columnNameMapping =
        ColumnNameMapping(
            mapOf(
                "bool_col" to "bool_col",
                "int_col" to "int_col",
                "num_col" to "num_col",
                "string_col" to "string_col",
                "date_col" to "date_col",
                "time_tz_col" to "time_tz_col",
                "time_no_tz_col" to "time_no_tz_col",
                "ts_tz_col" to "ts_tz_col",
                "ts_no_tz_col" to "ts_no_tz_col",
                "array_col" to "array_col",
                "obj_col" to "obj_col",
                "union_col" to "union_col",
                "unknown_col" to "unknown_col"
            )
        )
    private lateinit var formatter: ProtoToBigQueryStandardInsertRecordFormatter
    private lateinit var encoder: AirbyteValueProtobufEncoder

    @BeforeEach
    fun setUp() {
        encoder = AirbyteValueProtobufEncoder()
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
                field("unknown_col", UnknownType(Jsons.emptyObject()), 12),
            )

        fieldAccessors = fields.toTypedArray()

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
                encoder.encode(null, LeafAirbyteSchemaType.STRING),
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
                            false
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
                    "unknown_col" to FieldType(UnknownType(Jsons.emptyObject()), false)
                ),
            )

        stream = mockk {
            every { this@mockk.airbyteValueProxyFieldAccessors } returns fieldAccessors
            every { this@mockk.syncId } returns
                this@ProtoToBigQueryStandardInsertRecordFormatterTest.syncId
            every { this@mockk.generationId } returns
                this@ProtoToBigQueryStandardInsertRecordFormatterTest.generationId
            every { this@mockk.schema } returns dummyType
            every { this@mockk.mappedDescriptor } returns DestinationStream.Descriptor("", "dummy")
            every { this@mockk.unknownColumnChanges } returns
                dummyType.computeUnknownColumnChanges()
        }

        record =
            mockk(relaxed = true) {
                every { this@mockk.airbyteRawId } returns uuid
                every { this@mockk.rawData } returns protoSource!!
                every { this@mockk.stream } returns
                    this@ProtoToBigQueryStandardInsertRecordFormatterTest.stream
            }

        formatter =
            ProtoToBigQueryStandardInsertRecordFormatter(fieldAccessors, columnNameMapping, stream)
    }

    @AfterEach fun tearDown() = unmockkAll()

    @Test
    fun `formats BigQuery record with all field types`() {
        val jsonResult = formatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Verify meta fields
        assertEquals(uuid.toString(), result.get("_airbyte_raw_id").asText())
        assertNotNull(result.get("_airbyte_extracted_at").asText())
        assertEquals(generationId, result.get("_airbyte_generation_id").asLong())

        // Verify primitives
        assertEquals(true, result.get("bool_col").asBoolean())
        assertEquals(123L, result.get("int_col").asLong())
        assertEquals(12.34, result.get("num_col").asDouble(), 0.001)
        assertEquals("hello", result.get("string_col").asText())
        assertEquals("2025-06-17", result.get("date_col").asText())
        assertEquals("23:59:59+02:00", result.get("time_tz_col").asText())
        assertEquals("23:59:59", result.get("time_no_tz_col").asText())
        assertEquals("2025-06-17T23:59:59+02:00", result.get("ts_tz_col").asText())
        assertEquals("2025-06-17T23:59:59", result.get("ts_no_tz_col").asText())

        // Verify complex types
        val arrayCol = result.get("array_col") as ArrayNode
        assertEquals(2, arrayCol.size())
        assertEquals("a", arrayCol.get(0).asText())
        assertEquals("b", arrayCol.get(1).asText())

        val objCol = result.get("obj_col") as ObjectNode
        assertEquals("v", objCol.get("k").asText())

        val unionCol = result.get("union_col") as ObjectNode
        assertEquals(1, unionCol.get("u").asInt())

        // Verify unknown column is null
        assertTrue(result.get("unknown_col").isNull())

        // Verify meta field with changes
        val meta = result.get("_airbyte_meta") as ObjectNode
        assertEquals(syncId, meta.get("sync_id").asLong())

        val changes = meta.get("changes") as ArrayNode
        assertEquals(4, changes.size()) // 3 original + 1 unknown column

        // Original changes
        val change0 = changes.get(0) as ObjectNode
        assertEquals("x", change0.get("field").asText())
        assertEquals("NULLED", change0.get("change").asText())
        assertEquals("DESTINATION_SERIALIZATION_ERROR", change0.get("reason").asText())

        val change1 = changes.get(1) as ObjectNode
        assertEquals("y", change1.get("field").asText())
        assertEquals("NULLED", change1.get("change").asText())
        assertEquals("SOURCE_SERIALIZATION_ERROR", change1.get("reason").asText())

        val change2 = changes.get(2) as ObjectNode
        assertEquals("z", change2.get("field").asText())
        assertEquals("TRUNCATED", change2.get("change").asText())
        assertEquals("SOURCE_RECORD_SIZE_LIMITATION", change2.get("reason").asText())

        // Unknown column change
        val change3 = changes.get(3) as ObjectNode
        assertEquals("unknown_col", change3.get("field").asText())
        assertEquals("NULLED", change3.get("change").asText())
        assertEquals("DESTINATION_SERIALIZATION_ERROR", change3.get("reason").asText())
    }

    @Test
    fun `handles null values correctly`() {
        // Create a record with all null values
        val nullProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // bool_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // int_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // num_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // string_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // date_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // time_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // time_no_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // ts_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // ts_no_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // array_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // obj_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // union_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(), // unknown_col
            )

        val nullRecord = buildModifiedRecord(nullProtoValues)
        every { record.rawData } returns nullRecord

        val jsonResult = formatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // All user fields should be explicitly null in JSON
        assertTrue(result.get("bool_col").isNull())
        assertTrue(result.get("int_col").isNull())
        assertTrue(result.get("num_col").isNull())
        assertTrue(result.get("string_col").isNull())
        assertTrue(result.get("date_col").isNull())
        assertTrue(result.get("time_tz_col").isNull())
        assertTrue(result.get("time_no_tz_col").isNull())
        assertTrue(result.get("ts_tz_col").isNull())
        assertTrue(result.get("ts_no_tz_col").isNull())
        assertTrue(result.get("array_col").isNull())
        assertTrue(result.get("obj_col").isNull())
        assertTrue(result.get("union_col").isNull())
        assertTrue(result.get("unknown_col").isNull())

        // Meta fields should still be present and valid
        assertEquals(uuid.toString(), result.get("_airbyte_raw_id").asText())
        assertNotNull(result.get("_airbyte_extracted_at"))
        assertEquals(generationId, result.get("_airbyte_generation_id").asLong())
        assertNotNull(result.get("_airbyte_meta"))
    }

    @Test
    fun `handles integer overflow with proper error tracking`() {
        val bigInteger = BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE)
        val oversizedProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBoolean(true).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setBigInteger(bigInteger.toString())
                    .build(), // Oversized int
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setNumber(12.34).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("hello").build(),
                encoder.encode(LocalDate.parse("2025-06-17"), LeafAirbyteSchemaType.DATE).build(),
                encoder
                    .encode(
                        OffsetTime.parse("23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalTime.parse("23:59:59"),
                        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        OffsetDateTime.parse("2025-06-17T23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                    )
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
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(),
            )

        val oversizedRecord = buildModifiedRecord(oversizedProtoValues)
        every { record.rawData } returns oversizedRecord

        val jsonResult = formatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Integer field should be null due to overflow
        assertTrue(result.get("int_col").isNull())

        // Check that error was tracked in meta
        val meta = result.get("_airbyte_meta") as ObjectNode
        val changes = meta.get("changes") as ArrayNode

        // Should have original changes + unknown column change + integer overflow change
        assertEquals(5, changes.size())

        // Find the integer overflow change
        val intChange =
            changes.find { change -> (change as ObjectNode).get("field").asText() == "int_col" }
                as ObjectNode

        assertEquals("NULLED", intChange.get("change").asText())
        assertEquals("DESTINATION_FIELD_SIZE_LIMITATION", intChange.get("reason").asText())
    }

    @Test
    fun `handles invalid timestamp with proper error tracking`() {
        val invalidTimestampProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBoolean(true).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setInteger(123).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setNumber(12.34).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("hello").build(),
                encoder.encode(LocalDate.parse("2025-06-17"), LeafAirbyteSchemaType.DATE).build(),
                encoder
                    .encode(
                        OffsetTime.parse("23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalTime.parse("23:59:59"),
                        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                    )
                    .build(),
                // Invalid timestamp
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setTimestampWithTimezone(
                        AirbyteRecordMessage.OffsetDateTime.newBuilder()
                            .setEpochSecond(-999999999999L)
                            .setNano(-1)
                            .setOffsetSeconds(0)
                            .build()
                    )
                    .build(),
                encoder
                    .encode(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                    )
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
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(),
            )

        val invalidRecord = buildModifiedRecord(invalidTimestampProtoValues)
        every { record.rawData } returns invalidRecord

        val jsonResult = formatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Timestamp field should be null due to parsing error
        assertTrue(result.get("ts_tz_col").isNull())

        // Check that error was tracked in meta
        val meta = result.get("_airbyte_meta") as ObjectNode
        val changes = meta.get("changes") as ArrayNode

        // Should have original changes + unknown column change + timestamp parsing change
        assertEquals(5, changes.size())

        // Find the timestamp parsing change
        val timestampChange =
            changes.find { change -> (change as ObjectNode).get("field").asText() == "ts_tz_col" }
                as ObjectNode

        assertEquals("NULLED", timestampChange.get("change").asText())
        assertEquals("DESTINATION_FIELD_SIZE_LIMITATION", timestampChange.get("reason").asText())
    }

    @Test
    fun `throws when record is not protobuf`() {
        val nonProto =
            mockk<DestinationRecordRaw> {
                every { rawData } returns mockk<DestinationRecordSource>(relaxed = true)
            }

        val ex =
            assertThrows(IllegalArgumentException::class.java) { formatter.formatRecord(nonProto) }
        assertTrue(
            ex.message!!.contains(
                "ProtoToBigQueryRecordFormatter only supports DestinationRecordProtobufSource"
            )
        )
    }

    @Test
    fun `produces valid JSON structure`() {
        val jsonResult = formatter.formatRecord(record)

        // Should be valid JSON
        assertDoesNotThrow { jsonResult.deserializeToNode() }

        // Should start and end with braces
        assertTrue(jsonResult.startsWith("{"))
        assertTrue(jsonResult.endsWith("}"))

        // Should contain expected top-level fields
        assertTrue(jsonResult.contains("\"_airbyte_raw_id\""))
        assertTrue(jsonResult.contains("\"_airbyte_extracted_at\""))
        assertTrue(jsonResult.contains("\"_airbyte_generation_id\""))
        assertTrue(jsonResult.contains("\"_airbyte_meta\""))

        // Should contain user fields
        assertTrue(jsonResult.contains("\"bool_col\""))
        assertTrue(jsonResult.contains("\"string_col\""))
    }

    @Test
    fun `handles empty arrays and objects`() {
        val emptyComplexTypesProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBoolean(true).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setInteger(123).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setNumber(12.34).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("hello").build(),
                encoder.encode(LocalDate.parse("2025-06-17"), LeafAirbyteSchemaType.DATE).build(),
                encoder
                    .encode(
                        OffsetTime.parse("23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalTime.parse("23:59:59"),
                        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        OffsetDateTime.parse("2025-06-17T23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                    )
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setJson("""[]""".toByteArray().toByteString()) // Empty array
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setJson("""{}""".toByteArray().toByteString()) // Empty object
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setJson("""{"u":1}""".toByteArray().toByteString())
                    .build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(),
            )

        val emptyComplexRecord = buildModifiedRecord(emptyComplexTypesProtoValues)
        every { record.rawData } returns emptyComplexRecord

        val jsonResult = formatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Verify empty array
        val arrayCol = result.get("array_col") as ArrayNode
        assertEquals(0, arrayCol.size())

        // Verify empty object
        val objCol = result.get("obj_col") as ObjectNode
        assertEquals(0, objCol.size())
    }

    @Test
    fun `handles invalid date format with proper error tracking`() {
        val invalidDateProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBoolean(true).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setInteger(123).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setNumber(12.34).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("hello").build(),
                // Invalid date
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setDate(Integer.MAX_VALUE.toLong())
                    .build(),
                encoder
                    .encode(
                        OffsetTime.parse("23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalTime.parse("23:59:59"),
                        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        OffsetDateTime.parse("2025-06-17T23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                    )
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
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(),
            )

        val invalidDateRecord = buildModifiedRecord(invalidDateProtoValues)
        every { record.rawData } returns invalidDateRecord

        val jsonResult = formatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Date field should be null due to parsing error
        assertTrue(result.get("date_col").isNull())

        // Check that error was tracked in meta
        val meta = result.get("_airbyte_meta") as ObjectNode
        val changes = meta.get("changes") as ArrayNode

        // Should have original changes + unknown column change + date parsing change
        assertEquals(5, changes.size())

        // Find the date parsing change
        val dateChange =
            changes.find { change -> (change as ObjectNode).get("field").asText() == "date_col" }
                as ObjectNode

        assertEquals("NULLED", dateChange.get("change").asText())
        assertEquals("DESTINATION_FIELD_SIZE_LIMITATION", dateChange.get("reason").asText())
    }

    @Test
    fun `formats legacy raw table with validations applied`() {
        // Create a legacy formatter
        val legacyFormatter =
            ProtoToBigQueryStandardInsertRecordFormatter(
                fieldAccessors,
                columnNameMapping,
                stream,
                legacyRawTablesOnly = true
            )

        val jsonResult = legacyFormatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Verify meta fields are present
        assertEquals(uuid.toString(), result.get("_airbyte_raw_id").asText())
        assertNotNull(result.get("_airbyte_extracted_at").asText())
        assertEquals(generationId, result.get("_airbyte_generation_id").asLong())

        // Verify _airbyte_data column contains JSON string with validated data
        assertTrue(result.has("_airbyte_data"))
        val dataField = result.get("_airbyte_data").asText()

        // Parse the JSON data to verify it contains validated fields
        val dataJson = dataField.deserializeToNode() as ObjectNode

        // Verify all fields are present and validated
        assertEquals(true, dataJson.get("bool_col").asBoolean())
        assertEquals(123L, dataJson.get("int_col").asLong())
        assertEquals(12.34, dataJson.get("num_col").asDouble(), 0.001)
        assertEquals("hello", dataJson.get("string_col").asText())
        assertEquals("2025-06-17", dataJson.get("date_col").asText())
        assertEquals("23:59:59+02:00", dataJson.get("time_tz_col").asText())
        assertEquals("23:59:59", dataJson.get("time_no_tz_col").asText())
        assertEquals("2025-06-17T23:59:59+02:00", dataJson.get("ts_tz_col").asText())
        assertEquals("2025-06-17T23:59:59", dataJson.get("ts_no_tz_col").asText())

        // Verify complex types
        val arrayCol = dataJson.get("array_col") as ArrayNode
        assertEquals(2, arrayCol.size())
        assertEquals("a", arrayCol.get(0).asText())
        assertEquals("b", arrayCol.get(1).asText())

        val objCol = dataJson.get("obj_col") as ObjectNode
        assertEquals("v", objCol.get("k").asText())

        // Verify unknown column is null
        assertTrue(dataJson.get("unknown_col").isNull())

        // Verify meta field with changes (should include validation errors)
        // In legacy mode, _airbyte_meta is stored as JSON string, so we need to parse it
        val metaString = result.get("_airbyte_meta").asText()
        val meta = metaString.deserializeToNode() as ObjectNode
        assertEquals(syncId, meta.get("sync_id").asLong())

        val changes = meta.get("changes") as ArrayNode
        assertEquals(4, changes.size()) // 3 original + 1 unknown column
    }

    @Test
    fun `legacy mode applies integer overflow validation`() {
        val legacyFormatter =
            ProtoToBigQueryStandardInsertRecordFormatter(
                fieldAccessors,
                columnNameMapping,
                stream,
                legacyRawTablesOnly = true
            )

        val bigInteger = BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE)
        val oversizedProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBoolean(true).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setBigInteger(bigInteger.toString())
                    .build(), // Oversized int
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setNumber(12.34).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("hello").build(),
                encoder.encode(LocalDate.parse("2025-06-17"), LeafAirbyteSchemaType.DATE).build(),
                encoder
                    .encode(
                        OffsetTime.parse("23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalTime.parse("23:59:59"),
                        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        OffsetDateTime.parse("2025-06-17T23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                    )
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
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(),
            )

        val oversizedRecord = buildModifiedRecord(oversizedProtoValues)
        every { record.rawData } returns oversizedRecord

        val jsonResult = legacyFormatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Verify _airbyte_data column contains validated data
        val dataField = result.get("_airbyte_data").asText()
        val dataJson = dataField.deserializeToNode() as ObjectNode

        // Integer field should be null due to overflow
        assertTrue(dataJson.get("int_col").isNull())

        // Check that error was tracked in meta
        // In legacy mode, _airbyte_meta is stored as JSON string, so we need to parse it
        val metaString = result.get("_airbyte_meta").asText()
        val meta = metaString.deserializeToNode() as ObjectNode
        val changes = meta.get("changes") as ArrayNode

        // Should have original changes + unknown column change + integer overflow change
        assertEquals(5, changes.size())

        // Find the integer overflow change
        val intChange =
            changes.find { change -> (change as ObjectNode).get("field").asText() == "int_col" }
                as ObjectNode

        assertEquals("NULLED", intChange.get("change").asText())
        assertEquals("DESTINATION_FIELD_SIZE_LIMITATION", intChange.get("reason").asText())
    }

    @Test
    fun `legacy mode applies timestamp validation`() {
        val legacyFormatter =
            ProtoToBigQueryStandardInsertRecordFormatter(
                fieldAccessors,
                columnNameMapping,
                stream,
                legacyRawTablesOnly = true
            )

        val invalidTimestampProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBoolean(true).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setInteger(123).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setNumber(12.34).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("hello").build(),
                encoder.encode(LocalDate.parse("2025-06-17"), LeafAirbyteSchemaType.DATE).build(),
                encoder
                    .encode(
                        OffsetTime.parse("23:59:59+02:00"),
                        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                    )
                    .build(),
                encoder
                    .encode(
                        LocalTime.parse("23:59:59"),
                        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                    )
                    .build(),
                // Invalid timestamp
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setTimestampWithTimezone(
                        AirbyteRecordMessage.OffsetDateTime.newBuilder()
                            .setEpochSecond(-999999999999L)
                            .setNano(-1)
                            .setOffsetSeconds(0)
                            .build()
                    )
                    .build(),
                encoder
                    .encode(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                    )
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
                    .setNull(com.google.protobuf.NullValue.NULL_VALUE)
                    .build(),
            )

        val invalidRecord = buildModifiedRecord(invalidTimestampProtoValues)
        every { record.rawData } returns invalidRecord

        val jsonResult = legacyFormatter.formatRecord(record)
        val result = jsonResult.deserializeToNode() as ObjectNode

        // Verify _airbyte_data column contains validated data
        val dataField = result.get("_airbyte_data").asText()
        val dataJson = dataField.deserializeToNode() as ObjectNode

        // Timestamp field should be null due to parsing error
        assertTrue(dataJson.get("ts_tz_col").isNull())

        // Check that error was tracked in meta
        // In legacy mode, _airbyte_meta is stored as JSON string, so we need to parse it
        val metaString = result.get("_airbyte_meta").asText()
        val meta = metaString.deserializeToNode() as ObjectNode
        val changes = meta.get("changes") as ArrayNode

        // Should have original changes + unknown column change + timestamp parsing change
        assertEquals(5, changes.size())

        // Find the timestamp parsing change
        val timestampChange =
            changes.find { change -> (change as ObjectNode).get("field").asText() == "ts_tz_col" }
                as ObjectNode

        assertEquals("NULLED", timestampChange.get("change").asText())
        assertEquals("DESTINATION_FIELD_SIZE_LIMITATION", timestampChange.get("reason").asText())
    }

    @Test
    fun `legacy mode vs direct mode structure difference`() {
        val legacyFormatter =
            ProtoToBigQueryStandardInsertRecordFormatter(
                fieldAccessors,
                columnNameMapping,
                stream,
                legacyRawTablesOnly = true
            )

        val directFormatter =
            ProtoToBigQueryStandardInsertRecordFormatter(
                fieldAccessors,
                columnNameMapping,
                stream,
                legacyRawTablesOnly = false
            )

        val legacyResult = legacyFormatter.formatRecord(record).deserializeToNode() as ObjectNode
        val directResult = directFormatter.formatRecord(record).deserializeToNode() as ObjectNode

        // Legacy mode should have _airbyte_data field
        assertTrue(legacyResult.has("_airbyte_data"))
        assertFalse(directResult.has("_airbyte_data"))

        // Direct mode should have individual field columns
        assertTrue(directResult.has("bool_col"))
        assertTrue(directResult.has("string_col"))
        assertTrue(directResult.has("int_col"))

        // Legacy mode should NOT have individual field columns (only _airbyte_data)
        assertFalse(legacyResult.has("bool_col"))
        assertFalse(legacyResult.has("string_col"))
        assertFalse(legacyResult.has("int_col"))

        // Both should have the same metadata fields
        assertEquals(
            legacyResult.get("_airbyte_raw_id").asText(),
            directResult.get("_airbyte_raw_id").asText()
        )
        assertEquals(
            legacyResult.get("_airbyte_generation_id").asLong(),
            directResult.get("_airbyte_generation_id").asLong()
        )

        // Meta fields should have the same number of changes
        // In legacy mode, _airbyte_meta is stored as JSON string, so we need to parse it
        val legacyMetaString = legacyResult.get("_airbyte_meta").asText()
        val legacyMeta = legacyMetaString.deserializeToNode() as ObjectNode
        val directMeta = directResult.get("_airbyte_meta") as ObjectNode
        val legacyChanges = legacyMeta.get("changes") as ArrayNode
        val directChanges = directMeta.get("changes") as ArrayNode
        assertEquals(legacyChanges.size(), directChanges.size())
    }

    private fun buildModifiedRecord(
        protoValues: List<AirbyteRecordMessage.AirbyteValueProtobuf>
    ): DestinationRecordProtobufSource {
        val recordProto =
            AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                .mergeFrom(protoSource!!.source.record)
                .clearData()
                .addAllData(protoValues)
                .build()

        val msg = AirbyteMessage.AirbyteMessageProtobuf.newBuilder().setRecord(recordProto).build()
        return DestinationRecordProtobufSource(msg)
    }

    private fun field(
        name: String,
        type: io.airbyte.cdk.load.data.AirbyteType,
        idx: Int
    ): AirbyteValueProxy.FieldAccessor = mockk {
        every { this@mockk.name } returns name
        every { this@mockk.type } returns type
        try {
            every { this@mockk.index } returns idx
        } catch (_: Exception) {}
    }
}
