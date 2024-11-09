/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnionType
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
                    "union" to StringValue("hello"),
                    "combined_denormalized" to
                        ObjectValue(linkedMapOf("name" to StringValue("hello"))),
                    "union_array" to ArrayValue(listOf(StringValue("hello"), IntegerValue(42))),
                    "date" to DateValue("2021-01-01"),
                    "time" to TimeValue("12:00:00"),
                    "timestamp" to TimestampValue("2021-01-01T12:00:00Z"),
                    "time_without_timezone" to TimeValue("12:00:00"),
                    "timestamp_without_timezone" to TimestampValue("2021-01-01T12:00:00")
                )
            )
        val schema =
            ObjectType(
                linkedMapOf(
                    "name" to FieldType(StringType, true),
                    "age" to FieldType(IntegerType, false),
                    "is_cool" to FieldType(BooleanType, false),
                    "height" to FieldType(NumberType, false),
                    "friends" to FieldType(ArrayType(FieldType(StringType, true)), false),
                    "address" to
                        FieldType(
                            ObjectType(
                                linkedMapOf(
                                    "street" to FieldType(StringType, true),
                                    "city" to FieldType(StringType, true)
                                )
                            ),
                            false
                        ),
                    "union" to FieldType(UnionType.of(StringType, IntegerType), true),
                    "combined_denormalized" to
                        FieldType(
                            ObjectType(linkedMapOf("name" to FieldType(StringType, true))),
                            false
                        ),
                    "union_array" to
                        FieldType(
                            ArrayType(FieldType(UnionType.of(StringType, IntegerType), true)),
                            true
                        ),
                    "date" to FieldType(DateType, false),
                    "time" to FieldType(TimeTypeWithoutTimezone, false),
                    "timestamp" to FieldType(TimestampTypeWithoutTimezone, false),
                    "time_without_timezone" to FieldType(TimeTypeWithTimezone, false),
                    "timestamp_without_timezone" to FieldType(TimestampTypeWithTimezone, false)
                )
            )
        val jsonValue = AirbyteValueToJson().convert(airbyteValue)
        val roundTripValue = JsonToAirbyteValue().convert(jsonValue, schema)

        Assertions.assertEquals(airbyteValue, roundTripValue)
    }
}
