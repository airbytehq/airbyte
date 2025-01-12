/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

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
}
