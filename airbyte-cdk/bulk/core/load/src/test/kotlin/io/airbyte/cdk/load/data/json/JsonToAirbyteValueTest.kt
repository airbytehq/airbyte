/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullType
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
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonToAirbyteValueTest {
    @Test
    fun testNull() {
        val value = JsonToAirbyteValue().convert(JsonNodeFactory.instance.nullNode(), NullType)
        Assertions.assertTrue(value is NullValue)
    }

    @Test
    fun testString() {
        val value =
            JsonToAirbyteValue().convert(JsonNodeFactory.instance.textNode("hello"), StringType)
        Assertions.assertTrue(value is StringValue)
        Assertions.assertEquals("hello", (value as StringValue).value)
    }

    @Test
    fun testBoolean() {
        val value =
            JsonToAirbyteValue().convert(JsonNodeFactory.instance.booleanNode(true), BooleanType)
        Assertions.assertTrue(value is BooleanValue)
        Assertions.assertEquals(true, (value as BooleanValue).value)
    }

    @Test
    fun testInteger() {
        val value =
            JsonToAirbyteValue().convert(JsonNodeFactory.instance.numberNode(42), IntegerType)
        Assertions.assertTrue(value is IntegerValue)
        Assertions.assertEquals(42, (value as IntegerValue).value)
    }

    @Test
    fun testNumber() {
        val value =
            JsonToAirbyteValue().convert(JsonNodeFactory.instance.numberNode(42), NumberType)
        Assertions.assertTrue(value is NumberValue)
        Assertions.assertEquals(BigDecimal(42), (value as NumberValue).value)
    }

    @Test
    fun testArray() {
        val value =
            JsonToAirbyteValue()
                .convert(
                    JsonNodeFactory.instance.arrayNode().add("hello").add("world"),
                    ArrayType(FieldType(StringType, true))
                )
        Assertions.assertTrue(value is ArrayValue)
        val arrayValue = value as ArrayValue
        Assertions.assertEquals(2, arrayValue.values.size)
        Assertions.assertTrue(arrayValue.values[0] is StringValue)
        Assertions.assertEquals("hello", (arrayValue.values[0] as StringValue).value)
        Assertions.assertTrue(arrayValue.values[1] is StringValue)
        Assertions.assertEquals("world", (arrayValue.values[1] as StringValue).value)
    }

    @Test
    fun testArrayWithoutSchema() {
        val value =
            JsonToAirbyteValue()
                .convert(
                    JsonNodeFactory.instance.arrayNode().add("hello").add("world"),
                    ArrayTypeWithoutSchema
                )
        Assertions.assertTrue(value is ArrayValue, "Expected ArrayValue, got $value")
        val arrayValue = value as ArrayValue
        Assertions.assertEquals(2, arrayValue.values.size)
        Assertions.assertTrue(arrayValue.values[0] is StringValue)
        Assertions.assertEquals("hello", (arrayValue.values[0] as StringValue).value)
        Assertions.assertTrue(arrayValue.values[1] is StringValue)
        Assertions.assertEquals("world", (arrayValue.values[1] as StringValue).value)
    }

    @Test
    fun testObject() {
        val value =
            JsonToAirbyteValue()
                .convert(
                    JsonNodeFactory.instance.objectNode().put("name", "world"),
                    ObjectType(linkedMapOf("name" to FieldType(StringType, true)))
                )
        Assertions.assertTrue(value is ObjectValue)
        val objectValue = value as ObjectValue
        Assertions.assertEquals(1, objectValue.values.size)
        Assertions.assertTrue(objectValue.values["name"] is StringValue)
        Assertions.assertEquals("world", (objectValue.values["name"] as StringValue).value)
    }

    @Test
    fun testObjectWithoutSchema() {
        listOf(ObjectTypeWithoutSchema, ObjectTypeWithEmptySchema).forEach {
            val value =
                JsonToAirbyteValue()
                    .convert(JsonNodeFactory.instance.objectNode().put("name", "world"), it)
            Assertions.assertTrue(value is ObjectValue)
            val objectValue = value as ObjectValue
            Assertions.assertEquals(1, objectValue.values.size)
            Assertions.assertTrue(objectValue.values["name"] is StringValue)
            Assertions.assertEquals("world", (objectValue.values["name"] as StringValue).value)
        }
    }

    @Test
    fun testUnion() {
        val stringValue =
            JsonToAirbyteValue()
                .convert(
                    JsonNodeFactory.instance.textNode("hello"),
                    UnionType(listOf(StringType, IntegerType))
                )
        Assertions.assertTrue(stringValue is StringValue)
        Assertions.assertEquals("hello", (stringValue as StringValue).value)

        val intValue =
            JsonToAirbyteValue()
                .convert(
                    JsonNodeFactory.instance.numberNode(42),
                    UnionType(listOf(StringType, IntegerType))
                )
        Assertions.assertTrue(intValue is IntegerValue)
        Assertions.assertEquals(42, (intValue as IntegerValue).value)
    }

    @Test
    fun testDate() {
        val value =
            JsonToAirbyteValue().convert(JsonNodeFactory.instance.textNode("2021-01-01"), DateType)
        Assertions.assertTrue(value is DateValue)
        Assertions.assertEquals("2021-01-01", (value as DateValue).value)
    }

    @Test
    fun testTimestamp() {
        val value =
            JsonToAirbyteValue()
                .convert(
                    JsonNodeFactory.instance.textNode("2021-01-01T00:00:00Z"),
                    TimestampTypeWithTimezone
                )
        Assertions.assertTrue(value is TimestampValue)
        Assertions.assertEquals("2021-01-01T00:00:00Z", (value as TimestampValue).value)
    }

    @Test
    fun testTime() {
        val value =
            JsonToAirbyteValue()
                .convert(JsonNodeFactory.instance.textNode("00:00:00"), TimeTypeWithTimezone)
        Assertions.assertTrue(value is TimeValue)
        Assertions.assertEquals("00:00:00", (value as TimeValue).value)
    }

    @Test
    fun testMissingObjectField() {
        val value =
            JsonToAirbyteValue()
                .convert(
                    Jsons.readTree("""{"foo": 1}"""),
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "foo" to FieldType(IntegerType, nullable = true),
                                "bar" to FieldType(IntegerType, nullable = true),
                            )
                    )
                )
        Assertions.assertEquals(
            ObjectValue(linkedMapOf("foo" to IntegerValue(1))),
            value,
        )
    }
}
