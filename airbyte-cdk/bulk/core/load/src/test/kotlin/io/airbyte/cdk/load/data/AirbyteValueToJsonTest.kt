/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

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
                    "null_field" to NullValue,
                    "nullable_union" to IntegerValue(42),
                    "nonnullable_union" to StringValue("hello"),
                    "combined_null" to StringValue("hello"),
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
                    "null_field" to FieldType(NullType, false),
                    "nullable_union" to
                        FieldType(UnionType(listOf(StringType, IntegerType, NullType)), false),
                    "nonnullable_union" to
                        FieldType(UnionType(listOf(StringType, IntegerType)), true),
                    "combined_null" to FieldType(UnionType(listOf(StringType, NullType)), false),
                    "combined_denormalized" to
                        FieldType(
                            ObjectType(linkedMapOf("name" to FieldType(StringType, true))),
                            false
                        ),
                    "union_array" to
                        FieldType(
                            ArrayType(FieldType(UnionType(listOf(StringType, IntegerType)), true)),
                            true
                        ),
                    "date" to FieldType(DateType, false),
                    "time" to FieldType(TimeType(false), false),
                    "timestamp" to FieldType(TimestampType(false), false),
                    "time_without_timezone" to FieldType(TimeType(true), false),
                    "timestamp_without_timezone" to FieldType(TimestampType(true), false)
                )
            )
        val jsonValue = AirbyteValueToJson().convert(airbyteValue)
        val roundTripValue = JsonToAirbyteValue().convert(jsonValue, schema)

        Assertions.assertEquals(airbyteValue, roundTripValue)
    }
}
