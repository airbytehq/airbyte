/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

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
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
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
class ProtoToBigQueryCSVRowGeneratorTest {

    private val uuid: UUID = UUID.fromString("11111111-1111-1111-1111-111111111111")
    private val emittedAtMs = 1_724_438_400_000L
    private val syncId = 42L
    private val generationId = 314L

    private lateinit var stream: DestinationStream
    private var protoSource: DestinationRecordProtobufSource? = null
    private lateinit var record: DestinationRecordRaw
    private lateinit var fieldAccessors: Array<AirbyteValueProxy.FieldAccessor>
    private lateinit var header: Array<String>
    private lateinit var generator: ProtoToBigQueryCSVRowGenerator

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
                field("unknown_col", UnknownType(Jsons.emptyObject()), 12),
            )

        fieldAccessors = fields.toTypedArray()

        // Create header array with data fields + meta fields
        header =
            arrayOf(
                "bool_col",
                "int_col",
                "num_col",
                "string_col",
                "date_col",
                "time_tz_col",
                "time_no_tz_col",
                "ts_tz_col",
                "ts_no_tz_col",
                "array_col",
                "obj_col",
                "union_col",
                "unknown_col",
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_GENERATION_ID,
                Meta.COLUMN_NAME_AB_META
            )

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
            every { this@mockk.syncId } returns this@ProtoToBigQueryCSVRowGeneratorTest.syncId
            every { this@mockk.generationId } returns
                this@ProtoToBigQueryCSVRowGeneratorTest.generationId
            every { this@mockk.schema } returns dummyType
            every { this@mockk.mappedDescriptor } returns DestinationStream.Descriptor("", "dummy")
            every { this@mockk.unknownColumnChanges } returns
                dummyType.computeUnknownColumnChanges()
        }

        record =
            mockk(relaxed = true) {
                every { this@mockk.airbyteRawId } returns uuid
                every { this@mockk.rawData } returns protoSource!!
                every { this@mockk.stream } returns this@ProtoToBigQueryCSVRowGeneratorTest.stream
            }

        generator = ProtoToBigQueryCSVRowGenerator(header, stream, fieldAccessors)
    }

    @AfterEach fun tearDown() = unmockkAll()

    @Test
    fun `generates CSV row with all field types`() {
        val csvRow = generator.generate(record)

        // Verify array size
        assertEquals(header.size, csvRow.size)

        // Verify data fields (indices 0-12)
        assertEquals(true, csvRow[0]) // bool_col
        assertEquals(123L, csvRow[1]) // int_col
        assertEquals(12.34.toBigDecimal(), csvRow[2]) // num_col
        assertEquals("hello", csvRow[3]) // string_col
        assertEquals("2025-06-17", csvRow[4]) // date_col
        assertEquals("23:59:59+02:00", csvRow[5]) // time_tz_col
        assertEquals("23:59:59", csvRow[6]) // time_no_tz_col
        assertEquals("2025-06-17T23:59:59+02:00", csvRow[7]) // ts_tz_col
        assertEquals("2025-06-17T23:59:59", csvRow[8]) // ts_no_tz_col

        // Verify complex types (serialized to JSON strings)
        assertEquals("""["a","b"]""", csvRow[9]) // array_col
        assertEquals("""{"k":"v"}""", csvRow[10]) // obj_col
        assertEquals("""{"u":1}""", csvRow[11]) // union_col

        // Verify unknown column is NULL_MARKER
        assertEquals(BigQueryConsts.NULL_MARKER, csvRow[12]) // unknown_col

        // Verify meta fields
        assertEquals(uuid.toString(), csvRow[13]) // _airbyte_raw_id
        assertNotNull(csvRow[14]) // _airbyte_extracted_at
        assertTrue(csvRow[14].toString().isNotEmpty())
        assertEquals(generationId.toString(), csvRow[15]) // _airbyte_generation_id

        // Verify meta field contains JSON with changes
        val metaJson = csvRow[16].toString()
        assertTrue(metaJson.contains("\"sync_id\":$syncId"))
        assertTrue(metaJson.contains("\"changes\":["))
        assertTrue(metaJson.contains("\"field\":\"x\""))
        assertTrue(metaJson.contains("\"change\":\"NULLED\""))
        assertTrue(metaJson.contains("\"reason\":\"DESTINATION_SERIALIZATION_ERROR\""))
        assertTrue(
            metaJson.contains("\"field\":\"unknown_col\"")
        ) // Should include unknown column change
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

        val csvRow = generator.generate(record)

        // All user fields should be NULL_MARKER
        for (i in 0..12) {
            assertEquals(BigQueryConsts.NULL_MARKER, csvRow[i])
        }

        // Meta fields should still be valid
        assertEquals(uuid.toString(), csvRow[13]) // _airbyte_raw_id
        assertNotNull(csvRow[14]) // _airbyte_extracted_at
        assertEquals(generationId.toString(), csvRow[15]) // _airbyte_generation_id
        assertNotNull(csvRow[16]) // _airbyte_meta
    }

    @Test
    fun `handles integer overflow with proper error tracking`() {
        val bigInteger = BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE)
        val encoder = AirbyteValueProtobufEncoder()
        val oversizedProtoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setBigInteger(bigInteger.toString())
                    .build(), // Oversized int
                encoder.encode(12.34, LeafAirbyteSchemaType.NUMBER).build(),
                encoder.encode("hello", LeafAirbyteSchemaType.STRING).build(),
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
                encoder.encode("""["a","b"]""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"k":"v"}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"u":1}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode(null, LeafAirbyteSchemaType.STRING).build(),
            )

        val oversizedRecord = buildModifiedRecord(oversizedProtoValues)
        every { record.rawData } returns oversizedRecord

        val csvRow = generator.generate(record)

        // Integer field should be NULL_MARKER due to overflow
        assertEquals(BigQueryConsts.NULL_MARKER, csvRow[1]) // int_col

        // Check that error was tracked in meta
        val metaJson = csvRow[16].toString()
        assertTrue(metaJson.contains("\"field\":\"int_col\""))
        assertTrue(metaJson.contains("\"change\":\"NULLED\""))
        assertTrue(metaJson.contains("\"reason\":\"DESTINATION_FIELD_SIZE_LIMITATION\""))
    }

    @Test
    fun `handles invalid timestamp with proper error tracking`() {
        val invalidTimestamp =
            AirbyteRecordMessage.OffsetDateTime.newBuilder()
                .setEpochSecond(Long.MIN_VALUE)
                .setNano(Int.MIN_VALUE)
                .setOffsetSeconds(Int.MIN_VALUE)
                .build()
        val encoder = AirbyteValueProtobufEncoder()
        val invalidTimestampProtoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN).build(),
                encoder.encode(123L, LeafAirbyteSchemaType.INTEGER).build(),
                encoder.encode(12.34, LeafAirbyteSchemaType.NUMBER).build(),
                encoder.encode("hello", LeafAirbyteSchemaType.STRING).build(),
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
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setTimestampWithTimezone(invalidTimestamp)
                    .build(), // Invalid timestamp
                encoder
                    .encode(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                    )
                    .build(),
                encoder.encode("""["a","b"]""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"k":"v"}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"u":1}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode(null, LeafAirbyteSchemaType.STRING).build(),
            )

        val invalidRecord = buildModifiedRecord(invalidTimestampProtoValues)
        every { record.rawData } returns invalidRecord

        val csvRow = generator.generate(record)

        // Timestamp field should be NULL_MARKER due to parsing error
        assertEquals(BigQueryConsts.NULL_MARKER, csvRow[7]) // ts_tz_col

        // Check that error was tracked in meta
        val metaJson = csvRow[16].toString()
        assertTrue(metaJson.contains("\"field\":\"ts_tz_col\""))
        assertTrue(metaJson.contains("\"change\":\"NULLED\""))
        assertTrue(metaJson.contains("\"reason\":\"DESTINATION_SERIALIZATION_ERROR\""))
    }

    @Test
    fun `throws when record is not protobuf`() {
        val nonProto =
            mockk<DestinationRecordRaw> {
                every { rawData } returns mockk<DestinationRecordSource>(relaxed = true)
            }

        val ex = assertThrows(IllegalArgumentException::class.java) { generator.generate(nonProto) }
        assertTrue(
            ex.message!!.contains(
                "ProtoToBigQueryCSVRowGenerator only supports DestinationRecordProtobufSource"
            )
        )
    }

    @Test
    fun `produces correct array structure`() {
        val csvRow = generator.generate(record)

        // Should be an array with expected size
        assertTrue(csvRow.isNotEmpty())
        assertEquals(header.size, csvRow.size)

        // All elements should be non-null (even if they contain NULL_MARKER)
        csvRow.forEach { assertNotNull(it) }

        // Meta fields should be strings
        assertTrue(csvRow[13] is String) // _airbyte_raw_id
        assertTrue(csvRow[14] is String) // _airbyte_extracted_at
        assertTrue(csvRow[15] is String) // _airbyte_generation_id
        assertTrue(csvRow[16] is String) // _airbyte_meta
    }

    @Test
    fun `handles empty arrays and objects`() {
        val encoder = AirbyteValueProtobufEncoder()
        val emptyComplexTypesProtoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN).build(),
                encoder.encode(123L, LeafAirbyteSchemaType.INTEGER).build(),
                encoder.encode(12.34, LeafAirbyteSchemaType.NUMBER).build(),
                encoder.encode("hello", LeafAirbyteSchemaType.STRING).build(),
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
                encoder
                    .encode("""[]""".toByteArray(), LeafAirbyteSchemaType.JSONB)
                    .build(), // Empty array
                encoder
                    .encode("""{}""".toByteArray(), LeafAirbyteSchemaType.JSONB)
                    .build(), // Empty object
                encoder.encode("""{"u":1}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode(null, LeafAirbyteSchemaType.STRING).build(),
            )

        val emptyComplexRecord = buildModifiedRecord(emptyComplexTypesProtoValues)
        every { record.rawData } returns emptyComplexRecord

        val csvRow = generator.generate(record)

        // Verify empty array and object
        assertEquals("[]", csvRow[9]) // array_col
        assertEquals("{}", csvRow[10]) // obj_col
    }

    @Test
    fun `handles invalid date format with proper error tracking`() {
        val encoder = AirbyteValueProtobufEncoder()
        val invalidDateProtoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN).build(),
                encoder.encode(123L, LeafAirbyteSchemaType.INTEGER).build(),
                encoder.encode(12.34, LeafAirbyteSchemaType.NUMBER).build(),
                encoder.encode("hello", LeafAirbyteSchemaType.STRING).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setDate(Long.MIN_VALUE) // Invalid date format
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
                encoder.encode("""["a","b"]""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"k":"v"}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"u":1}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode(null, LeafAirbyteSchemaType.STRING).build(),
            )

        val invalidDateRecord = buildModifiedRecord(invalidDateProtoValues)
        every { record.rawData } returns invalidDateRecord

        val csvRow = generator.generate(record)

        // Date field should be NULL_MARKER due to parsing error
        assertEquals(BigQueryConsts.NULL_MARKER, csvRow[4]) // date_col

        // Check that error was tracked in meta
        val metaJson = csvRow[16].toString()
        assertTrue(metaJson.contains("\"field\":\"date_col\""))
        assertTrue(metaJson.contains("\"change\":\"NULLED\""))
        assertTrue(metaJson.contains("\"reason\":\"DESTINATION_SERIALIZATION_ERROR\""))
    }

    @Test
    fun `handles large numeric values with truncation`() {
        val encoder = AirbyteValueProtobufEncoder()
        val largeNumericProtoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN).build(),
                encoder.encode(123L, LeafAirbyteSchemaType.INTEGER).build(),
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNumber(1.2345678901234568E29)
                    .build(), // Large number that might need truncation
                encoder.encode("hello", LeafAirbyteSchemaType.STRING).build(),
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
                encoder.encode("""["a","b"]""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"k":"v"}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode("""{"u":1}""".toByteArray(), LeafAirbyteSchemaType.JSONB).build(),
                encoder.encode(null, LeafAirbyteSchemaType.STRING).build(),
            )

        val largeNumericRecord = buildModifiedRecord(largeNumericProtoValues)
        every { record.rawData } returns largeNumericRecord

        val csvRow = generator.generate(record)

        // Numeric field should either be truncated or nulled depending on BigQuery limits
        // The exact behavior depends on BigQueryRecordFormatter validation logic
        assertNotNull(csvRow[2]) // num_col should be handled somehow

        // If there was validation/truncation, it should be tracked in meta
        val metaJson = csvRow[16].toString()

        val metaAsNode = metaJson.deserializeToNode()
        assertEquals(42, metaAsNode["sync_id"].asInt())
        assertEquals(5, metaAsNode["changes"].size())
    }

    @Test
    fun `uses BigQuery NULL_MARKER for missing values`() {
        val csvRow = generator.generate(record)

        // Unknown column should use NULL_MARKER
        assertEquals(BigQueryConsts.NULL_MARKER, csvRow[12]) // unknown_col

        // Verify NULL_MARKER is the expected BigQuery constant
        assertNotEquals("null", BigQueryConsts.NULL_MARKER)
        assertNotEquals(null, BigQueryConsts.NULL_MARKER)
    }

    @Test
    fun `preserves field order based on header array`() {
        val csvRow = generator.generate(record)

        // Verify that field order matches header order
        assertEquals("bool_col", header[0])
        assertEquals("int_col", header[1])
        assertEquals("num_col", header[2])

        // The actual values should be in the same positions
        assertEquals(true, csvRow[0])
        assertEquals(123L, csvRow[1])
        assertEquals(12.34.toBigDecimal(), csvRow[2])

        // Meta fields should be at the end
        val rawIdIndex = header.indexOf(Meta.COLUMN_NAME_AB_RAW_ID)
        val extractedAtIndex = header.indexOf(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
        val generationIdIndex = header.indexOf(Meta.COLUMN_NAME_AB_GENERATION_ID)
        val metaIndex = header.indexOf(Meta.COLUMN_NAME_AB_META)

        assertEquals(uuid.toString(), csvRow[rawIdIndex])
        assertNotNull(csvRow[extractedAtIndex])
        assertEquals(generationId.toString(), csvRow[generationIdIndex])
        assertNotNull(csvRow[metaIndex])
    }

    @Test
    fun `handles out-of-range timestamps`() {
        val encoder = AirbyteValueProtobufEncoder()
        val protoData =
            listOf(
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(
                        OffsetDateTime.parse("9999-12-31T23:00:00-08"),
                        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                    ),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                    encoder.encode(null, LeafAirbyteSchemaType.STRING),
                )
                .map { it.build() }
        val csvRow =
            generator.generate(
                mockk(relaxed = true) {
                    every { this@mockk.airbyteRawId } returns uuid
                    every { this@mockk.rawData } returns
                        DestinationRecordProtobufSource(
                            AirbyteMessage.AirbyteMessageProtobuf.newBuilder()
                                .setRecord(
                                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                                        .setStreamName("dummy")
                                        .setEmittedAtMs(emittedAtMs)
                                        .addAllData(protoData)
                                        .setMeta(
                                            AirbyteRecordMessageMetaOuterClass
                                                .AirbyteRecordMessageMeta
                                                .newBuilder()
                                                .build()
                                        )
                                        .build()
                                )
                                .build()
                        )
                    every { this@mockk.stream } returns
                        this@ProtoToBigQueryCSVRowGeneratorTest.stream
                }
            )
        assertEquals("\\N", csvRow[7])
        assertEquals(
            // unknown column is always nulled, b/c proto mode doesn't support unknown types.
            // more importantly, we null out the ts_tz field with DESTINATION_FIELD_SIZE_LIMITATION.
            """{"sync_id":42,"changes":[{"field":"unknown_col","change":"NULLED","reason":"DESTINATION_SERIALIZATION_ERROR"},{"field":"ts_tz_col","change":"NULLED","reason":"DESTINATION_FIELD_SIZE_LIMITATION"}]}""",
            csvRow[16],
        )
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
