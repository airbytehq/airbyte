/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
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
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.util.UUID
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class ProtobufConverterTest {

    private val encoder = AirbyteValueProtobufEncoder()

    private fun createMockCoercerPassThrough(): ValueCoercer =
        mockk<ValueCoercer> {
            every { representAs(any()) } returns null
            every { map(any()) } answers { firstArg<EnrichedAirbyteValue>() }
            every { validate(any()) } returns ValidationResult.Valid
        }

    private fun fa(name: String, type: AirbyteType, idx: Int): FieldAccessor = mockk {
        every { this@mockk.name } returns name
        every { this@mockk.type } returns type
        every { this@mockk.index } returns idx
    }

    private fun vBoolean(b: Boolean) = encoder.encode(b, LeafAirbyteSchemaType.BOOLEAN)

    private fun vInteger(i: Long) = encoder.encode(i, LeafAirbyteSchemaType.INTEGER)

    private fun vBigInteger(str: String) =
        encoder.encode(BigInteger(str), LeafAirbyteSchemaType.INTEGER)

    private fun vNumber(d: Double) = encoder.encode(d, LeafAirbyteSchemaType.NUMBER)

    private fun vBigDecimal(str: String) =
        encoder.encode(BigDecimal(str), LeafAirbyteSchemaType.NUMBER)

    private fun vString(s: String) = encoder.encode(s, LeafAirbyteSchemaType.STRING)

    private fun vDate(date: LocalDate) = encoder.encode(date, LeafAirbyteSchemaType.DATE)

    private fun vTimeTz(time: OffsetTime) =
        encoder.encode(time, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)

    private fun vTimeNoTz(time: LocalTime) =
        encoder.encode(time, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)

    private fun vTsTz(ts: OffsetDateTime) =
        encoder.encode(ts, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)

    private fun vTsNoTz(ts: LocalDateTime) =
        encoder.encode(ts, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)

    private fun vJson(json: String) = encoder.encode(json, LeafAirbyteSchemaType.JSONB)

    private fun vNull() = encoder.encode(null, LeafAirbyteSchemaType.STRING)

    /** Build a real DestinationRecordProtobufSource without mocking the value class. */
    private fun buildProtoSource(
        values: List<AirbyteRecordMessage.AirbyteValueProtobuf>,
        emittedAtMs: Long = System.currentTimeMillis(),
        metaChanges: List<AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange> =
            emptyList()
    ): DestinationRecordProtobufSource {
        val metaProto =
            AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMeta.newBuilder()
                .addAllChanges(metaChanges)
                .build()

        val recordProto: AirbyteRecordMessageProtobuf =
            AirbyteRecordMessageProtobuf.newBuilder()
                .setStreamName("dummy")
                .setEmittedAtMs(emittedAtMs)
                .addAllData(values)
                .setMeta(metaProto)
                .build()

        val msg: AirbyteMessageProtobuf =
            AirbyteMessageProtobuf.newBuilder().setRecord(recordProto).build()

        return DestinationRecordProtobufSource(msg)
    }

    private fun metaChange(
        field: String,
        change: AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType,
        reason: AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
    ) =
        AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange.newBuilder()
            .setField(field)
            .setChange(change)
            .setReason(reason)
            .build()

    private fun mockMsgWithStream(
        accessors: Array<FieldAccessor>,
        source: DestinationRecordProtobufSource = buildProtoSource(emptyList()),
        generationId: Long = 1L,
        syncId: Long = 2L,
        unknownChanges: List<Meta.Change> = emptyList(),
        columnNameMapper: ((String) -> String)? = null
    ): DestinationRecordRaw {
        val destinationStream =
            mockk<DestinationStream> {
                every { airbyteValueProxyFieldAccessors } returns accessors
                every { this@mockk.generationId } returns generationId
                every { this@mockk.syncId } returns syncId
                every { unknownColumnChanges } returns unknownChanges
                every { mappedDescriptor } returns DestinationStream.Descriptor("namespace", "name")
                every { unmappedDescriptor } returns
                    DestinationStream.Descriptor("namespace", "name")
                // Add tableSchema mock
                every { tableSchema } returns
                    mockk {
                        every { getFinalColumnName(any()) } answers
                            {
                                val columnName = firstArg<String>()
                                columnNameMapper?.invoke(columnName) ?: columnName
                            }
                    }
            }
        return mockk<DestinationRecordRaw> {
            every { stream } returns destinationStream
            every { airbyteRawId } returns UUID.randomUUID()
            every { rawData } returns source
        }
    }

    @Test
    fun `convertWithMetadata processes basic types correctly`() {
        val valueCoercer = createMockCoercerPassThrough()
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors =
            arrayOf(
                fa("string_field", StringType, 0),
                fa("boolean_field", BooleanType, 1),
                fa("integer_field", IntegerType, 2),
                fa("number_field", NumberType, 3),
                fa("bigdecimal_field", NumberType, 4),
                fa("date_field", DateType, 5),
                fa("time_tz_field", TimeTypeWithTimezone, 6),
                fa("time_no_tz_field", TimeTypeWithoutTimezone, 7),
                fa("ts_tz_field", TimestampTypeWithTimezone, 8),
                fa("ts_no_tz_field", TimestampTypeWithoutTimezone, 9),
                fa("array_field", ArrayType(FieldType(StringType, false)), 10),
                fa("obj_field", ObjectType(linkedMapOf("k" to FieldType(StringType, false))), 11),
                fa(
                    "union_field",
                    UnionType.of(ObjectType(linkedMapOf("u" to FieldType(IntegerType, false)))),
                    12
                ),
                fa("unknown_field", UnknownType(Jsons.emptyObject()), 13)
            )

        val protoValues =
            listOf(
                vString("test_string"),
                vBoolean(true),
                vInteger(123),
                vNumber(45.67),
                vBigDecimal("999.12345"),
                vDate(LocalDate.parse("2025-06-17")),
                vTimeTz(OffsetTime.of(LocalTime.parse("23:59:59"), ZoneOffset.ofHours(2))),
                vTimeNoTz(LocalTime.parse("23:59:59")),
                vTsTz(
                    OffsetDateTime.of(
                        LocalDateTime.parse("2025-06-17T23:59:59"),
                        ZoneOffset.ofHours(2)
                    )
                ),
                vTsNoTz(LocalDateTime.parse("2025-06-17T23:59:59")),
                vJson("""["a","b"]"""),
                vJson("""{"k":"v"}"""),
                vJson("""{"u":1}"""),
                vNull()
            )

        val msg = mockMsgWithStream(accessors, buildProtoSource(protoValues.map { it.build() }))
        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))

        assertTrue(result["string_field"] is StringValue)
        assertEquals("test_string", (result["string_field"] as StringValue).value)

        assertTrue(result["boolean_field"] is BooleanValue)
        assertEquals(true, (result["boolean_field"] as BooleanValue).value)

        assertTrue(result["integer_field"] is IntegerValue)
        assertEquals(BigInteger.valueOf(123), (result["integer_field"] as IntegerValue).value)

        assertTrue(result["number_field"] is NumberValue)
        assertEquals(BigDecimal.valueOf(45.67), (result["number_field"] as NumberValue).value)

        assertTrue(result["bigdecimal_field"] is NumberValue)
        assertEquals(BigDecimal("999.12345"), (result["bigdecimal_field"] as NumberValue).value)

        assertTrue(result["date_field"] is DateValue)
        assertEquals("2025-06-17", (result["date_field"] as DateValue).value.toString())

        assertTrue(result["time_tz_field"] is TimeWithTimezoneValue)
        assertEquals(
            "23:59:59+02:00",
            (result["time_tz_field"] as TimeWithTimezoneValue).value.toString()
        )

        assertTrue(result["time_no_tz_field"] is TimeWithoutTimezoneValue)
        assertEquals(
            "23:59:59",
            (result["time_no_tz_field"] as TimeWithoutTimezoneValue).value.toString()
        )

        assertTrue(result["ts_tz_field"] is TimestampWithTimezoneValue)
        assertEquals(
            "2025-06-17T23:59:59+02:00",
            (result["ts_tz_field"] as TimestampWithTimezoneValue).value.toString()
        )

        assertTrue(result["ts_no_tz_field"] is TimestampWithoutTimezoneValue)
        assertEquals(
            "2025-06-17T23:59:59",
            (result["ts_no_tz_field"] as TimestampWithoutTimezoneValue).value.toString()
        )

        assertTrue(result.containsKey("array_field"))
        assertTrue(result.containsKey("obj_field"))
        assertTrue(result.containsKey("union_field"))

        assertFalse(result.containsKey("unknown_field"))

        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_GENERATION_ID))
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_RAW_ID))
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_META))

        verify { valueCoercer.map(any()) }
        verify { valueCoercer.validate(any()) }
    }

    @Test
    fun `convertWithMetadata handles BigDecimal values correctly`() {
        val valueCoercer = createMockCoercerPassThrough()
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors =
            arrayOf(
                fa("small_decimal", NumberType, 0),
                fa("large_decimal", NumberType, 1),
                fa("scientific_decimal", NumberType, 2),
                fa("negative_decimal", NumberType, 3)
            )

        val protoValues =
            listOf(
                vBigDecimal("0.0001"),
                vBigDecimal("123456789.987654321"),
                vBigDecimal("1.23E-10"),
                vBigDecimal("-999.999")
            )

        val msg =
            mockMsgWithStream(accessors, source = buildProtoSource(protoValues.map { it.build() }))
        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))

        assertTrue(result["small_decimal"] is NumberValue)
        assertEquals(BigDecimal("0.0001"), (result["small_decimal"] as NumberValue).value)

        assertTrue(result["large_decimal"] is NumberValue)
        assertEquals(
            BigDecimal("123456789.987654321"),
            (result["large_decimal"] as NumberValue).value
        )

        assertTrue(result["scientific_decimal"] is NumberValue)
        assertEquals(BigDecimal("1.23E-10"), (result["scientific_decimal"] as NumberValue).value)

        assertTrue(result["negative_decimal"] is NumberValue)
        assertEquals(BigDecimal("-999.999"), (result["negative_decimal"] as NumberValue).value)
    }

    @Test
    fun `convertWithMetadata handles null values`() {
        val valueCoercer = createMockCoercerPassThrough()
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors = arrayOf(fa("null_field", StringType, 0))

        val protoValues = listOf(vNull())

        val msg =
            mockMsgWithStream(accessors, source = buildProtoSource(protoValues.map { it.build() }))
        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))
        assertTrue(result.containsKey("null_field"))
        assertEquals(NullValue, result["null_field"])
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_META))
    }

    @Test
    fun `convertWithMetadata applies type representation override`() {
        val valueCoercer =
            mockk<ValueCoercer> {
                every { representAs(ofType(TimeTypeWithoutTimezone::class)) } returns
                    StringValue::class.java
                every { representAs(not(ofType(TimeTypeWithoutTimezone::class))) } returns null
                every { map(any()) } answers { firstArg<EnrichedAirbyteValue>() }
                every { validate(any()) } returns ValidationResult.Valid
            }
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors = arrayOf(fa("time_field", TimeTypeWithoutTimezone, 0))
        val protoValues = listOf(vTimeNoTz(LocalTime.parse("12:34:56")))

        val msg =
            mockMsgWithStream(accessors, source = buildProtoSource(protoValues.map { it.build() }))

        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))

        assertTrue(result["time_field"] is StringValue)
        assertEquals("12:34:56", (result["time_field"] as StringValue).value)
        verify { valueCoercer.representAs(ofType(TimeTypeWithoutTimezone::class)) }
    }

    @Test
    fun `convertWithMetadata applies valueCoercer mapping and validation`() {
        val valueCoercer =
            mockk<ValueCoercer> {
                every { representAs(any()) } returns null
                every { map(any()) } answers
                    {
                        val enriched = firstArg<EnrichedAirbyteValue>()
                        if (enriched.abValue is StringValue) {
                            enriched.abValue =
                                StringValue((enriched.abValue as StringValue).value.uppercase())
                        }
                        enriched
                    }
                every { validate(any()) } answers
                    {
                        val enriched = firstArg<EnrichedAirbyteValue>()
                        if (
                            enriched.abValue is StringValue &&
                                (enriched.abValue as StringValue).value.length > 5
                        ) {
                            ValidationResult.ShouldNullify(
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION
                            )
                        } else {
                            ValidationResult.Valid
                        }
                    }
            }
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors = arrayOf(fa("short_string", StringType, 0), fa("long_string", StringType, 1))
        val protoValues = listOf(vString("hello"), vString("this_is_too_long"))

        val msg =
            mockMsgWithStream(accessors, source = buildProtoSource(protoValues.map { it.build() }))

        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))

        assertTrue(result["short_string"] is StringValue)
        assertEquals("HELLO", (result["short_string"] as StringValue).value)

        assertTrue(result.containsKey("long_string"))
        assertEquals(NullValue, result["long_string"])
    }

    @Test
    fun `convertWithMetadata applies column mapping`() {
        val valueCoercer = createMockCoercerPassThrough()
        // NOTE: Column name mapping is now handled by the stream's tableSchema
        // This test has been modified to work with the new API
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors = arrayOf(fa("original_name", StringType, 0))
        val protoValues = listOf(vString("test"))

        val msg =
            mockMsgWithStream(
                accessors,
                source = buildProtoSource(protoValues.map { it.build() }),
                columnNameMapper = { columnName ->
                    if (columnName == "original_name") "mapped_name" else columnName
                }
            )

        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))

        // Column mapping is now handled by tableSchema
        assertFalse(result.containsKey("original_name"))
        assertTrue(result.containsKey("mapped_name"))
        assertEquals("test", (result["mapped_name"] as StringValue).value)
    }

    @Test
    fun `convertWithMetadata handles parsing exceptions`() {
        val valueCoercer = createMockCoercerPassThrough()
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors = arrayOf(fa("invalid_int", IntegerType, 0))

        val invalidBigInteger =
            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBigInteger("boom!").build()
        val protoValues = listOf(invalidBigInteger)

        val msg = mockMsgWithStream(accessors, source = buildProtoSource(protoValues))

        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))

        assertTrue(result.containsKey("invalid_int"))
        assertEquals(NullValue, result["invalid_int"])
        assertTrue(result.containsKey(Meta.COLUMN_NAME_AB_META))
        val meta = result[Meta.COLUMN_NAME_AB_META] as ObjectValue
        val changes = meta.values["changes"] as ArrayValue
        assertEquals(1, changes.values.size)
    }

    @Test
    fun `convertWithMetadata merges meta changes from source + stream unknown changes + parsing failures`() {
        val valueCoercer = createMockCoercerPassThrough()
        val validationResultHandler = ValidationResultHandler(mockk(relaxed = true))
        val converter = ProtobufConverter(valueCoercer, validationResultHandler)

        val accessors = arrayOf(fa("ok_str", StringType, 0), fa("bad_int", IntegerType, 1))

        val sourceSideChanges =
            listOf(
                metaChange(
                    "x",
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED,
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .DESTINATION_SERIALIZATION_ERROR
                ),
                metaChange(
                    "y",
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED,
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_SERIALIZATION_ERROR
                )
            )

        val invalidBigInteger =
            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBigInteger("boom!")

        val protoValues = listOf(vString("hello"), invalidBigInteger)

        val unknownColumnChanges =
            listOf(
                Meta.Change(
                    "unknown_field",
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_SERIALIZATION_ERROR
                )
            )

        val msg =
            mockMsgWithStream(
                accessors,
                unknownChanges = unknownColumnChanges,
                source =
                    buildProtoSource(
                        protoValues.map { it.build() },
                        metaChanges = sourceSideChanges
                    )
            )

        val result = converter.convert(ConversionInput(msg, PartitionKey("test-key")))

        val meta = result[Meta.COLUMN_NAME_AB_META] as ObjectValue
        val changes = meta.values["changes"] as ArrayValue
        assertTrue(changes.values.size >= 4)
    }
}
