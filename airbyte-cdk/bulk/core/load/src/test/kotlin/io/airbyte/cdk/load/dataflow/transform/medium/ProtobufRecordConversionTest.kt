/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import com.google.protobuf.NullValue
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.computeUnknownColumnChanges
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.ProtobufTypeMismatchException
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.dataflow.transform.data.ValidationResultHandler
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import io.mockk.every
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.unmockkAll
import java.math.BigInteger
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.util.UUID
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ProtobufRecordConversionTest {

    private val encoder = AirbyteValueProtobufEncoder()
    private val uuid: UUID = UUID.fromString("11111111-1111-1111-1111-111111111111")
    private val emittedAtMs = 1_724_438_400_000L
    private val syncId = 42L
    private val generationId = 314L

    private lateinit var stream: DestinationStream
    private lateinit var valueCoercer: ValueCoercer
    private lateinit var validationResultHandler: ValidationResultHandler
    private var protoSource: DestinationRecordProtobufSource? = null
    private lateinit var record: DestinationRecordRaw
    private lateinit var fieldAccessors: Array<AirbyteValueProxy.FieldAccessor>
    private lateinit var converter: ProtobufConverter

    @BeforeEach
    fun setUp() {
        // NOTE: Column name mapping is now handled by the stream's tableSchema

        valueCoercer =
            object : ValueCoercer {
                val INT64_MAX = BigInteger(Long.MAX_VALUE.toString())
                val INT64_MIN = BigInteger(Long.MIN_VALUE.toString())
                override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
                    return value
                }

                override fun validate(value: EnrichedAirbyteValue): ValidationResult =
                    when (val abValue = value.abValue) {
                        is IntegerValue ->
                            if (abValue.value !in INT64_MIN..INT64_MAX) {
                                ValidationResult.ShouldNullify(
                                    AirbyteRecordMessageMetaChange.Reason
                                        .DESTINATION_FIELD_SIZE_LIMITATION,
                                )
                            } else {
                                ValidationResult.Valid
                            }
                        else -> {
                            ValidationResult.Valid
                        }
                    }
            }

        validationResultHandler = ValidationResultHandler(mockk(relaxed = true))

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
                encoder.encode("""["a","b"]""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"k":"v"}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"u":1}""", LeafAirbyteSchemaType.JSONB),
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
            every { this@mockk.syncId } returns this@ProtobufRecordConversionTest.syncId
            every { this@mockk.generationId } returns this@ProtobufRecordConversionTest.generationId
            every { this@mockk.schema } returns dummyType
            every { this@mockk.mappedDescriptor } returns DestinationStream.Descriptor("", "dummy")
            every { this@mockk.unmappedDescriptor } returns
                DestinationStream.Descriptor("", "dummy")
            every { this@mockk.unknownColumnChanges } returns
                dummyType.computeUnknownColumnChanges()
            // Add tableSchema mock for column name mapping
            every { this@mockk.tableSchema } returns
                mockk {
                    every { getFinalColumnName(any()) } answers
                        {
                            val columnName = firstArg<String>()
                            "mapped_$columnName"
                        }
                }
        }

        record =
            mockk(relaxed = false) {
                every { asJsonRecord() } answers { callOriginal() }
                every { asEnrichedDestinationRecordAirbyteValue(any(), any()) } answers
                    {
                        callOriginal()
                    }
                every { this@mockk.airbyteRawId } returns uuid
                every { this@mockk.schema } returns this@ProtobufRecordConversionTest.stream.schema
                every { this@mockk.schemaFields } returns
                    (this@ProtobufRecordConversionTest.stream.schema as ObjectType).properties
                every { this@mockk.rawData } returns protoSource!!
                every { this@mockk.stream } returns this@ProtobufRecordConversionTest.stream
            }

        converter = ProtobufConverter(valueCoercer, validationResultHandler)
    }

    @AfterEach fun tearDown() = unmockkAll()

    @Test
    fun `transforms protobuf record with all field types`() {
        val result = converter.convert(ConversionInput(record, PartitionKey("test-key")))

        assertEquals(16, result.size)

        // Verify all expected user field keys are present
        val expectedUserFields =
            setOf(
                "mapped_bool_col",
                "mapped_int_col",
                "mapped_num_col",
                "mapped_string_col",
                "mapped_date_col",
                "mapped_time_tz_col",
                "mapped_time_no_tz_col",
                "mapped_ts_tz_col",
                "mapped_ts_no_tz_col",
                "mapped_array_col",
                "mapped_obj_col",
                "mapped_union_col"
            )
        val actualUserFields = result.keys.filter { !it.startsWith("_airbyte_") }.toSet()
        assertEquals(expectedUserFields, actualUserFields)

        // Verify primitive field types and exact values
        val boolValue = result["mapped_bool_col"] as BooleanValue
        assertEquals(true, boolValue.value)

        val intValue = result["mapped_int_col"] as IntegerValue
        assertEquals(123L.toBigInteger(), intValue.value)

        val numValue = result["mapped_num_col"] as NumberValue
        assertEquals(12.34.toBigDecimal(), numValue.value)

        val strValue = result["mapped_string_col"] as StringValue
        assertEquals("hello", strValue.value)

        val dateValue = result["mapped_date_col"] as DateValue
        assertEquals(LocalDate.of(2025, 6, 17), dateValue.value)

        // Verify time and timestamp fields with precise types and values
        val timeWithTzValue = result["mapped_time_tz_col"] as TimeWithTimezoneValue
        assertEquals(OffsetTime.parse("23:59:59+02:00"), timeWithTzValue.value)

        val timeWithoutTzValue = result["mapped_time_no_tz_col"] as TimeWithoutTimezoneValue
        assertEquals(LocalTime.parse("23:59:59"), timeWithoutTzValue.value)

        val tsWithTzValue = result["mapped_ts_tz_col"] as TimestampWithTimezoneValue
        assertEquals(OffsetDateTime.parse("2025-06-17T23:59:59+02:00"), tsWithTzValue.value)

        val tsWithoutTzValue = result["mapped_ts_no_tz_col"] as TimestampWithoutTimezoneValue
        assertEquals(LocalDateTime.parse("2025-06-17T23:59:59"), tsWithoutTzValue.value)

        // Verify complex types are returned as AirbyteValue objects (not JSON strings)
        val arrayValue = result["mapped_array_col"] as ArrayValue
        assertEquals(2, arrayValue.values.size)
        assertEquals("a", (arrayValue.values[0] as StringValue).value)
        assertEquals("b", (arrayValue.values[1] as StringValue).value)

        val objValue = result["mapped_obj_col"] as ObjectValue
        assertEquals(1, objValue.values.size)
        assertEquals("v", (objValue.values["k"] as StringValue).value)

        val unionValue = result["mapped_union_col"] as ObjectValue
        assertEquals(1, unionValue.values.size)
        assertEquals(1L.toBigInteger(), (unionValue.values["u"] as IntegerValue).value)

        // Verify all Airbyte metadata fields are present with correct types
        val rawIdValue = result[Meta.COLUMN_NAME_AB_RAW_ID] as StringValue
        assertEquals(uuid.toString(), rawIdValue.value)

        val extractedAtValue =
            result[Meta.COLUMN_NAME_AB_EXTRACTED_AT] as TimestampWithTimezoneValue
        val expectedTimestamp =
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(emittedAtMs), ZoneOffset.UTC)
        assertEquals(expectedTimestamp, extractedAtValue.value)

        val generationIdValue = result[Meta.COLUMN_NAME_AB_GENERATION_ID] as IntegerValue
        assertEquals(generationId.toBigInteger(), generationIdValue.value)

        // Verify meta field has correct ObjectValue structure with sync_id and changes
        val metaValue = result[Meta.COLUMN_NAME_AB_META] as ObjectValue
        assertEquals(2, metaValue.values.size)
        assertTrue(metaValue.values.containsKey("sync_id"))
        assertTrue(metaValue.values.containsKey("changes"))

        val syncIdValue = metaValue.values["sync_id"] as IntegerValue
        assertEquals(syncId.toBigInteger(), syncIdValue.value)

        val changesArray = metaValue.values["changes"] as ArrayValue
        assertEquals(4, changesArray.values.size) // 3 source + 1 unknown column change

        // Verify each change object structure
        changesArray.values.forEachIndexed { index, change ->
            val changeObj = change as ObjectValue
            assertEquals(3, changeObj.values.size)
            assertTrue(changeObj.values.containsKey("field"))
            assertTrue(changeObj.values.containsKey("change"))
            assertTrue(changeObj.values.containsKey("reason"))

            val fieldValue = changeObj.values["field"] as StringValue
            val changeType = changeObj.values["change"] as StringValue
            val reasonValue = changeObj.values["reason"] as StringValue

            when (index) {
                0 -> {
                    assertEquals("x", fieldValue.value)
                    assertEquals("NULLED", changeType.value)
                    assertEquals("DESTINATION_SERIALIZATION_ERROR", reasonValue.value)
                }
                1 -> {
                    assertEquals("y", fieldValue.value)
                    assertEquals("NULLED", changeType.value)
                    assertEquals("SOURCE_SERIALIZATION_ERROR", reasonValue.value)
                }
                2 -> {
                    assertEquals("z", fieldValue.value)
                    assertEquals("TRUNCATED", changeType.value)
                    assertEquals("SOURCE_RECORD_SIZE_LIMITATION", reasonValue.value)
                }
                3 -> {
                    assertEquals("unknown_col", fieldValue.value)
                    assertEquals("NULLED", changeType.value)
                    assertEquals("DESTINATION_SERIALIZATION_ERROR", reasonValue.value)
                }
            }
        }
    }

    @Test
    fun `handles null values correctly`() {
        val nullProtoValues =
            mutableListOf(
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // bool_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // int_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // num_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // string_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // date_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // time_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // time_no_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // ts_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // ts_no_tz_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // array_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // obj_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // union_col
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                    .setNull(NullValue.NULL_VALUE)
                    .build(), // unknown_col
            )

        val nullRecord = buildModifiedRecord(nullProtoValues)
        every { record.rawData } returns nullRecord

        val result = converter.convert(ConversionInput(record, PartitionKey("test-key")))

        // All user fields should be excluded when null
        assertTrue(result.containsKey("mapped_bool_col"))
        assertTrue(result.get("mapped_bool_col") is io.airbyte.cdk.load.data.NullValue)
        assertTrue(result.containsKey("mapped_int_col"))
        assertTrue(result.get("mapped_int_col") is io.airbyte.cdk.load.data.NullValue)
        assertTrue(result.containsKey("mapped_num_col"))
        assertTrue(result.get("mapped_num_col") is io.airbyte.cdk.load.data.NullValue)
        assertTrue(result.containsKey("mapped_string_col"))
        assertTrue(result.get("mapped_string_col") is io.airbyte.cdk.load.data.NullValue)

        // Meta fields should still be present
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_RAW_ID))
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_GENERATION_ID))
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_META))
    }

    @Test
    fun `handles integer overflow with proper error tracking`() {
        val bigInteger = BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE)
        val oversizedProtoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN),
                encoder.encode(bigInteger, LeafAirbyteSchemaType.INTEGER), // Oversized int
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
                encoder.encode("""["a","b"]""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"k":"v"}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"u":1}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode(null, LeafAirbyteSchemaType.STRING),
            )

        val oversizedRecord = buildModifiedRecord(oversizedProtoValues.map { it.build() })
        every { record.rawData } returns oversizedRecord

        val result = converter.convert(ConversionInput(record, PartitionKey("test-key")))

        assertTrue(result.containsKey("mapped_int_col"))
        assertTrue(result.get("mapped_int_col") is io.airbyte.cdk.load.data.NullValue)

        // Check that error was tracked in meta object
        val metaValue = result[Meta.COLUMN_NAME_AB_META] as ObjectValue
        val changesArray = metaValue.values["changes"] as ArrayValue
        assertTrue(changesArray.values.isNotEmpty())

        // Verify that parsing failure is present in the changes
        val changes = changesArray.values.filterIsInstance<ObjectValue>()
        val intColError = changes.find { (it.values["field"] as StringValue).value == "int_col" }
        assertNotNull(intColError)
        assertEquals("NULLED", (intColError!!.values["change"] as StringValue).value)
        assertEquals(
            "DESTINATION_FIELD_SIZE_LIMITATION",
            (intColError.values["reason"] as StringValue).value
        )
    }

    @Test
    fun `handles invalid timestamp with proper error tracking`() {
        // Create an invalid timestamp using a manually crafted protobuf value
        // that will fail parsing in the decoder
        val invalidTimestampValue =
            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                .setTimestampWithTimezone(
                    AirbyteRecordMessage.OffsetDateTime.newBuilder()
                        .setEpochSecond(Long.MAX_VALUE) // Invalid - will cause overflow
                        .setNano(999999999)
                        .setOffsetSeconds(7200)
                        .build()
                )

        val invalidTimestampProtoValues =
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
                invalidTimestampValue, // Invalid timestamp
                encoder.encode(
                    LocalDateTime.parse("2025-06-17T23:59:59"),
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                ),
                encoder.encode("""["a","b"]""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"k":"v"}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"u":1}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode(null, LeafAirbyteSchemaType.STRING),
            )

        val invalidRecord = buildModifiedRecord(invalidTimestampProtoValues.map { it.build() })
        every { record.rawData } returns invalidRecord

        val result = converter.convert(ConversionInput(record, PartitionKey("test-key")))

        // Timestamp field should be excluded due to parsing error
        assertTrue(result.containsKey("mapped_ts_tz_col"))
        assertTrue(result.get("mapped_ts_tz_col") is io.airbyte.cdk.load.data.NullValue)

        // Check that error was tracked in meta object
        val metaValue = result[Meta.COLUMN_NAME_AB_META] as ObjectValue
        val changesArray = metaValue.values["changes"] as ArrayValue
        assertTrue(changesArray.values.isNotEmpty())

        // Verify that parsing failure is present in the changes
        val changes = changesArray.values.filterIsInstance<ObjectValue>()
        val timestampError =
            changes.find { (it.values["field"] as StringValue).value == "ts_tz_col" }
        assertNotNull(timestampError)
        assertEquals("NULLED", (timestampError!!.values["change"] as StringValue).value)
        assertEquals(
            "DESTINATION_SERIALIZATION_ERROR",
            (timestampError.values["reason"] as StringValue).value
        )
    }

    @Test
    fun `produces correct map structure`() {
        val result = converter.convert(ConversionInput(record, PartitionKey("test-key")))

        // Should be a map with expected keys
        assertTrue(result.isNotEmpty())

        // All values should be AirbyteValue instances (guaranteed by type system)
        assertTrue(result.values.isNotEmpty())

        // Meta fields should be present and have correct types
        assertTrue(result[Meta.COLUMN_NAME_AB_RAW_ID] is StringValue)
        assertTrue(result[Meta.COLUMN_NAME_AB_EXTRACTED_AT] is TimestampWithTimezoneValue)
        assertTrue(result[Meta.COLUMN_NAME_AB_GENERATION_ID] is IntegerValue)
        assertTrue(result[Meta.COLUMN_NAME_AB_META] is ObjectValue)
    }

    @Test
    fun `handles empty arrays and objects`() {
        val emptyComplexTypesProtoValues =
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
                encoder.encode("""[]""", LeafAirbyteSchemaType.JSONB), // Empty array
                encoder.encode("""{}""", LeafAirbyteSchemaType.JSONB), // Empty object
                encoder.encode("""{"u":1}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode(null, LeafAirbyteSchemaType.STRING),
            )

        val emptyComplexRecord =
            buildModifiedRecord(emptyComplexTypesProtoValues.map { it.build() })
        every { record.rawData } returns emptyComplexRecord

        val result = converter.convert(ConversionInput(record, PartitionKey("test-key")))

        // Verify empty array and object as AirbyteValue objects
        val emptyArrayValue = result["mapped_array_col"] as ArrayValue
        assertEquals(0, emptyArrayValue.values.size)

        val emptyObjValue = result["mapped_obj_col"] as ObjectValue
        assertEquals(0, emptyObjValue.values.size)
    }

    @Test
    fun `throws ProtobufTypeMismatchException when date field uses wrong setter`() {
        // Create an invalid date using setString() instead of the proper date setter
        val invalidDateValue =
            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setString("invalid-date")

        val invalidDateProtoValues =
            mutableListOf(
                encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN),
                encoder.encode(123L, LeafAirbyteSchemaType.INTEGER),
                encoder.encode(12.34, LeafAirbyteSchemaType.NUMBER),
                encoder.encode("hello", LeafAirbyteSchemaType.STRING),
                invalidDateValue, // Wrong setter used - should use date setter, not setString()
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
                encoder.encode("""["a","b"]""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"k":"v"}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode("""{"u":1}""", LeafAirbyteSchemaType.JSONB),
                encoder.encode(null, LeafAirbyteSchemaType.STRING),
            )

        val invalidDateRecord = buildModifiedRecord(invalidDateProtoValues.map { it.build() })
        every { record.rawData } returns invalidDateRecord

        // Assert that ProtobufTypeMismatchException is thrown
        val exception =
            assertThrows(ProtobufTypeMismatchException::class.java) {
                converter.convert(ConversionInput(record, PartitionKey("test-key")))
            }

        // Verify the error message contains expected information
        assertTrue(exception.message!!.contains("stream 'dummy'"))
        assertTrue(exception.message!!.contains("column 'date_col'"))
        assertTrue(exception.message!!.contains("Expected AirbyteType: DateType"))
        assertTrue(exception.message!!.contains("Actual protobuf ValueCase: STRING"))
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

    private fun field(name: String, type: AirbyteType, idx: Int): AirbyteValueProxy.FieldAccessor =
        mockk {
            every { this@mockk.name } returns name
            every { this@mockk.type } returns type
            try {
                every { this@mockk.index } returns idx
            } catch (_: Exception) {}
        }
}
