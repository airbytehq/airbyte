/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonToAirbyteValueTest {

    @Test
    fun testString() {
        val value = JsonToAirbyteValue().convert(JsonNodeFactory.instance.textNode("hello"))
        Assertions.assertTrue(value is StringValue)
        Assertions.assertEquals("hello", (value as StringValue).value)
    }

    @Test
    fun testBoolean() {
        val value = JsonToAirbyteValue().convert(JsonNodeFactory.instance.booleanNode(true))
        Assertions.assertTrue(value is BooleanValue)
        Assertions.assertEquals(true, (value as BooleanValue).value)
    }

    @Test
    fun testInteger() {
        val value = JsonToAirbyteValue().convert(JsonNodeFactory.instance.numberNode(42))
        Assertions.assertTrue(value is IntegerValue)
        Assertions.assertEquals(BigInteger.valueOf(42), (value as IntegerValue).value)
    }

    @Test
    fun testNumber() {
        val value = JsonToAirbyteValue().convert(JsonNodeFactory.instance.numberNode(42.1))
        Assertions.assertTrue(value is NumberValue)
        Assertions.assertEquals(BigDecimal("42.1"), (value as NumberValue).value)
    }

    @Test
    fun testArray() {
        val value =
            JsonToAirbyteValue()
                .convert(JsonNodeFactory.instance.arrayNode().add("hello").add("world"))
        Assertions.assertTrue(value is ArrayValue)
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
            JsonToAirbyteValue().convert(JsonNodeFactory.instance.objectNode().put("name", "world"))
        Assertions.assertTrue(value is ObjectValue)
        val objectValue = value as ObjectValue
        Assertions.assertEquals(1, objectValue.values.size)
        Assertions.assertTrue(objectValue.values["name"] is StringValue)
        Assertions.assertEquals("world", (objectValue.values["name"] as StringValue).value)
    }
}
