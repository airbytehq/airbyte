/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToString
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

class AirbyteValueToJsonTest {
    @Test
    fun testRoundTrip() {
        val airbyteValue =
            ObjectValue(
                linkedMapOf(
                    "name" to StringValue("hello"),
                    "age" to IntegerValue(42),
                    "is_cool" to BooleanValue(true),
                    "height" to NumberValue("42.0".toBigDecimal()),
                    "friends" to ArrayValue(listOf(StringValue("hello"), StringValue("world"))),
                    "address" to
                        ObjectValue(
                            linkedMapOf(
                                "street" to StringValue("123 Main St"),
                                "city" to StringValue("San Francisco")
                            )
                        ),
                )
            )
        val jsonValue = AirbyteValueToJson().convert(airbyteValue)
        val roundTripValue = JsonToAirbyteValue().convert(jsonValue)

        Assertions.assertEquals(airbyteValue, roundTripValue)
    }

    /**
     * We have some code that relies on being able to directly Jackson-serialize an AirbyteValue
     * (for example, the [serializeToString] extension method). Verify that this behaves correctly.
     */
    @Test
    fun testAllTypesSerialization() {
        val testCases: Map<AirbyteValue, String> =
            mapOf(
                NullValue to "null",
                StringValue("foo") to "\"foo\"",
                BooleanValue(true) to "true",
                IntegerValue(BigInteger("42")) to "42",
                NumberValue(BigDecimal("42.1")) to "42.1",
                DateValue(LocalDate.parse("2024-01-23")) to "\"2024-01-23\"",
                TimestampWithTimezoneValue(OffsetDateTime.parse("2024-01-23T12:34:56.78Z")) to
                    "\"2024-01-23T12:34:56.780Z\"",
                TimestampWithoutTimezoneValue(LocalDateTime.parse("2024-01-23T12:34:56.78")) to
                    "\"2024-01-23T12:34:56.780\"",
                TimeWithTimezoneValue(OffsetTime.parse("12:34:56.78Z")) to "\"12:34:56.780Z\"",
                TimeWithoutTimezoneValue(LocalTime.parse("12:34:56.78")) to "\"12:34:56.780\"",
                ArrayValue(listOf(NullValue, ArrayValue(listOf(NullValue)))) to "[null,[null]]",
                ObjectValue(linkedMapOf("foo" to ObjectValue(linkedMapOf("bar" to NullValue)))) to
                    """{"foo":{"bar":null}}""",
                UnknownValue(Jsons.readTree("""{"foo": "bar"}""")) to """{"foo":"bar"}"""
            )
        testCases.forEach { (value, expectedSerialization) ->
            val actual =
                assertDoesNotThrow("Failed to serialize $value") { Jsons.writeValueAsString(value) }
            assertEquals(expectedSerialization, actual, "Incorrect serialization for $value")
        }
    }
}
