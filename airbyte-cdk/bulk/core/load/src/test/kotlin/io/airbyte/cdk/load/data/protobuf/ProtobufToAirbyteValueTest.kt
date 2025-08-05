/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.protobuf

import com.google.protobuf.kotlin.toByteStringUtf8
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
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
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.mockk.mockk
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

internal class ProtobufToAirbyteValueTest {

    @Test
    fun testString() {
        val fieldName = "testString"
        val expectedValue = "testValue"
        val stream = createStream(fieldName = fieldName, fieldType = StringType)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setString(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is StringValue)
        assertEquals(expectedValue, (value.values[fieldName] as StringValue).value)
    }

    @Test
    fun testBoolean() {
        val fieldName = "testBoolean"
        val expectedValue = true
        val stream = createStream(fieldName = fieldName, fieldType = BooleanType)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setBoolean(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is BooleanValue)
        assertEquals(expectedValue, (value.values[fieldName] as BooleanValue).value)
    }

    @Test
    fun testInteger() {
        val fieldName = "testInteger"
        val expectedValue = 1L
        val stream = createStream(fieldName = fieldName, fieldType = IntegerType)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setInteger(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is IntegerValue)
        assertEquals(expectedValue.toBigInteger(), (value.values[fieldName] as IntegerValue).value)
    }

    @Test
    fun testNumber() {
        val fieldName = "testNumber"
        val expectedValue = 1.0
        val stream = createStream(fieldName = fieldName, fieldType = NumberType)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setNumber(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is NumberValue)
        assertEquals(expectedValue.toBigDecimal(), (value.values[fieldName] as NumberValue).value)
    }

    @Test
    fun testObject() {
        val fieldName = "testObject"
        val expectedValue = "{\"name\":\"testObject\"}"
        val stream =
            createStream(
                fieldName = fieldName,
                fieldType =
                    ObjectType(properties = linkedMapOf("name" to FieldType(StringType, false)))
            )
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setJson(expectedValue.toByteStringUtf8())
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is ObjectValue)
        assertEquals(
            "testObject",
            ((value.values[fieldName] as ObjectValue).values["name"] as StringValue).value
        )
    }

    @Test
    fun testArray() {
        val fieldName = "testArray"
        val expectedValue = "{\"name\":\"testObject\"}"
        val stream =
            createStream(
                fieldName = fieldName,
                fieldType = ArrayType(FieldType(StringType, false)),
            )
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setJson(expectedValue.toByteStringUtf8())
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is ObjectValue)
        assertEquals(
            "testObject",
            ((value.values[fieldName] as ObjectValue).values["name"] as StringValue).value
        )
    }

    @Test
    fun testArrayWithoutSchema() {
        val fieldName = "testArrayWithoutSchema"
        val expectedValue = "{\"name\":\"testObject\"}"
        val stream =
            createStream(
                fieldName = fieldName,
                fieldType = ArrayTypeWithoutSchema,
            )
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setJson(expectedValue.toByteStringUtf8())
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is ObjectValue)
        assertEquals(
            "testObject",
            ((value.values[fieldName] as ObjectValue).values["name"] as StringValue).value
        )
    }

    @Test
    fun testUnion() {
        val fieldName = "testUnion"
        val expectedValue = "{\"name\":\"testObject\"}"
        val stream =
            createStream(
                fieldName = fieldName,
                fieldType = UnionType(setOf(StringType), false),
            )
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setJson(expectedValue.toByteStringUtf8())
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is ObjectValue)
        assertEquals(
            "testObject",
            ((value.values[fieldName] as ObjectValue).values["name"] as StringValue).value
        )
    }

    @Test
    fun testObjectWithEmptySchema() {
        val fieldName = "testObjectWithEmptySchema"
        val expectedValue = "{\"name\":\"testObject\"}"
        val stream =
            createStream(
                fieldName = fieldName,
                fieldType = ObjectTypeWithEmptySchema,
            )
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setJson(expectedValue.toByteStringUtf8())
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is ObjectValue)
        assertEquals(
            "testObject",
            ((value.values[fieldName] as ObjectValue).values["name"] as StringValue).value
        )
    }

    @Test
    fun testObjectWithoutSchema() {
        val fieldName = "testObjectWithoutSchema"
        val expectedValue = "{\"name\":\"testObject\"}"
        val stream =
            createStream(
                fieldName = fieldName,
                fieldType = ObjectTypeWithoutSchema,
            )
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setJson(expectedValue.toByteStringUtf8())
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is ObjectValue)
        assertEquals(
            "testObject",
            ((value.values[fieldName] as ObjectValue).values["name"] as StringValue).value
        )
    }

    @Test
    fun testDate() {
        val fieldName = "testDate"
        val expectedValue = "2025-01-01"
        val stream = createStream(fieldName = fieldName, fieldType = DateType)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setDate(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is DateValue)
        assertEquals(LocalDate.parse(expectedValue), (value.values[fieldName] as DateValue).value)
    }

    @Test
    fun testTimeWithTimezone() {
        val fieldName = "testTimeWithTimezone"
        val expectedValue = "10:15:30+01:00"
        val stream = createStream(fieldName = fieldName, fieldType = TimeTypeWithTimezone)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setTimeWithTimezone(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is TimeWithTimezoneValue)
        assertEquals(
            OffsetTime.parse(expectedValue),
            (value.values[fieldName] as TimeWithTimezoneValue).value
        )
    }

    @Test
    fun testTimeWithoutTimezone() {
        val fieldName = "testTimeWithoutTimezone"
        val expectedValue = "10:15:30"
        val stream = createStream(fieldName = fieldName, fieldType = TimeTypeWithoutTimezone)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setTimeWithoutTimezone(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is TimeWithoutTimezoneValue)
        assertEquals(
            LocalTime.parse(expectedValue),
            (value.values[fieldName] as TimeWithoutTimezoneValue).value
        )
    }

    @Test
    fun testTimestampWithTimezone() {
        val fieldName = "testTimestampWithTimezone"
        val expectedValue = "2007-12-03T10:15:30+01:00"
        val stream = createStream(fieldName = fieldName, fieldType = TimestampTypeWithTimezone)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setTimestampWithTimezone(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is TimestampWithTimezoneValue)
        assertEquals(
            OffsetDateTime.parse(expectedValue),
            (value.values[fieldName] as TimestampWithTimezoneValue).value
        )
    }

    @Test
    fun testTimestampWithoutTimezone() {
        val fieldName = "testTimestampWithoutTimezone"
        val expectedValue = "2007-12-03T10:15:30"
        val stream = createStream(fieldName = fieldName, fieldType = TimestampTypeWithoutTimezone)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setTimestampWithoutTimezone(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is TimestampWithoutTimezoneValue)
        assertEquals(
            LocalDateTime.parse(expectedValue),
            (value.values[fieldName] as TimestampWithoutTimezoneValue).value
        )
    }

    @Test
    fun testNull() {
        val fieldName = "testString"
        val stream = createStream(fieldName = fieldName, fieldType = StringType)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setIsNull(true)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is NullValue)
    }

    @Test
    fun testNullValueForMissingValues() {
        val stream =
            DestinationStream(
                unmappedNamespace = null,
                unmappedName = "test",
                importType = Append,
                schema =
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "field1" to FieldType(BooleanType, false),
                                "field2" to FieldType(IntegerType, false),
                                "field3" to FieldType(NumberType, false),
                                "field4" to FieldType(DateType, false),
                                "field5" to
                                    FieldType(ObjectType(properties = linkedMapOf()), false),
                                "field6" to FieldType(StringType, false),
                                "field7" to FieldType(TimeTypeWithTimezone, false),
                                "field8" to FieldType(TimeTypeWithoutTimezone, false),
                                "field9" to FieldType(TimestampTypeWithTimezone, false),
                                "field10" to FieldType(TimestampTypeWithoutTimezone, false),
                            )
                    ),
                generationId = 1L,
                minimumGenerationId = 1L,
                syncId = 1L,
                namespaceMapper = mockk<NamespaceMapper>(relaxed = true),
                isFileBased = false,
                includeFiles = false,
                destinationObjectName = null,
                matchingKey = null,
            )
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val rawData = DestinationRecordProtobufSource(source = protobuf)
        val value =
            ProtobufToAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors).convert(rawData)

        assertTrue(value is ObjectValue)
        assertEquals(0, (value as ObjectValue).values.filter { it.value !is NullValue }.count())
    }

    @Test
    fun testExtensionFunction() {
        val fieldName = "testString"
        val expectedValue = "testValue"
        val stream = createStream(fieldName = fieldName, fieldType = StringType)
        val protobuf =
            AirbyteMessageProtobuf.newBuilder()
                .setRecord(
                    AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                        .setStreamName("test")
                        .setEmittedAtMs(1234)
                        .addData(
                            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                                .setString(expectedValue)
                        )
                        .setPartitionId("checkpoint_id")
                        .build()
                )
                .build()
        val value =
            DestinationRecordProtobufSource(source = protobuf)
                .toAirbyteValue(fields = stream.airbyteValueProxyFieldAccessors)

        assertTrue(value is ObjectValue)
        assertTrue((value as ObjectValue).values[fieldName] is StringValue)
        assertEquals(expectedValue, (value.values[fieldName] as StringValue).value)
    }

    private fun createStream(fieldName: String, fieldType: AirbyteType): DestinationStream {
        val properties = LinkedHashMap<String, FieldType>()
        properties.put(fieldName, FieldType(fieldType, false))
        return DestinationStream(
            unmappedNamespace = null,
            unmappedName = "test",
            importType = Append,
            schema = ObjectType(properties = properties),
            generationId = 1L,
            minimumGenerationId = 1L,
            syncId = 1L,
            namespaceMapper = mockk<NamespaceMapper>(relaxed = true),
            isFileBased = false,
            includeFiles = false,
            destinationObjectName = null,
            matchingKey = null,
        )
    }
}
