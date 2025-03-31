/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.AirbyteValueDeepCoercingMapper.Companion.DATE_TIME_FORMATTER
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import org.junit.jupiter.api.Assertions.assertAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class AirbyteValueDeepCoercingMapperTest {
    private val mapper =
        AirbyteValueDeepCoercingMapper(
            recurseIntoObjects = false,
            recurseIntoArrays = false,
            recurseIntoUnions = false,
        )

    @Test
    fun testBasicCoerce() {
        val (mappedValue, changes) =
            mapper.map(
                Jsons.readTree(
                        """
                    {
                      "undeclared": 42,
                      "null": null,
                      "string": "foo",
                      "boolean": true,
                      "integer": 42,
                      "number": 42.1,
                      "date": "2024-01-23",
                      "timestamptz": "2024-01-23T01:23:45Z",
                      "timestampntz": "2024-01-23T01:23:45",
                      "timetz": "01:23:45Z",
                      "timentz": "01:23:45",
                      "array": [1, 2, 3],
                      "array_schemaless": [1, true, "foo"],
                      "object": {"foo": 42},
                      "object_schemaless": {"foo": 42},
                      "object_empty": {"foo": 42}
                    }
                """.trimIndent()
                    )
                    .toAirbyteValue(),
                ObjectType(
                    linkedMapOf(
                        "null" to f(IntegerType),
                        "string" to f(StringType),
                        "boolean" to f(BooleanType),
                        "integer" to f(IntegerType),
                        "number" to f(NumberType),
                        "date" to f(DateType),
                        "timestamptz" to f(TimestampTypeWithTimezone),
                        "timestampntz" to f(TimestampTypeWithoutTimezone),
                        "timetz" to f(TimeTypeWithTimezone),
                        "timentz" to f(TimeTypeWithoutTimezone),
                        "array" to f(ArrayType(f(IntegerType))),
                        "array_schemaless" to f(ArrayTypeWithoutSchema),
                        "object" to f(ObjectType(linkedMapOf("foo" to f(IntegerType)))),
                        "object_schemaless" to f(ObjectTypeWithoutSchema),
                        "object_empty" to f(ObjectTypeWithEmptySchema),
                    )
                ),
            )
        assertAll(
            {
                assertEquals(
                    ObjectValue(
                        linkedMapOf(
                            // note that the undeclared field is now gone
                            "null" to NullValue,
                            "string" to StringValue("foo"),
                            "boolean" to BooleanValue(true),
                            "integer" to IntegerValue(42),
                            "number" to NumberValue(BigDecimal("42.1")),
                            "date" to DateValue(LocalDate.parse("2024-01-23")),
                            "timestamptz" to
                                TimestampWithTimezoneValue(
                                    OffsetDateTime.parse("2024-01-23T01:23:45Z")
                                ),
                            "timestampntz" to
                                TimestampWithoutTimezoneValue(
                                    LocalDateTime.parse("2024-01-23T01:23:45")
                                ),
                            "timetz" to TimeWithTimezoneValue(OffsetTime.parse("01:23:45Z")),
                            "timentz" to TimeWithoutTimezoneValue(LocalTime.parse("01:23:45")),
                            "array" to
                                ArrayValue(
                                    listOf(IntegerValue(1), IntegerValue(2), IntegerValue(3))
                                ),
                            "array_schemaless" to
                                ArrayValue(
                                    listOf(IntegerValue(1), BooleanValue(true), StringValue("foo"))
                                ),
                            "object" to ObjectValue(linkedMapOf("foo" to IntegerValue(42))),
                            "object_schemaless" to
                                ObjectValue(linkedMapOf("foo" to IntegerValue(42))),
                            "object_empty" to ObjectValue(linkedMapOf("foo" to IntegerValue(42))),
                        )
                    ),
                    mappedValue
                )
            },
            { assertEquals(emptyList<Meta.Change>(), changes) },
        )
    }

    @Test
    fun testCoerceDate() {
        listOf(
                "2021-1-1",
                "2021-01-01",
                "2021/01/02",
                "2021.01.03",
                "2021 Jan 04",
                "2021-1-1 BC",
            )
            .map { it to LocalDate.parse(it, DATE_TIME_FORMATTER) }
            .forEach { (input, localDate) ->
                val (value, changes) = mapper.map(StringValue(input), DateType)
                assertAll(
                    "Failed for input $input",
                    { assertEquals(DateValue(localDate), value) },
                    { assertEquals(emptyList<Meta.Change>(), changes) }
                )
            }
    }

    private val timestampPairs: List<Pair<String, OffsetDateTime>> =
        listOf(
            "2018-09-15 12:00:00" to
                LocalDateTime.parse("2018-09-15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2018-09-15 12:00:00.006542" to
                LocalDateTime.parse("2018-09-15 12:00:00.006542", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2018/09/15 12:00:00" to
                LocalDateTime.parse("2018/09/15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2018.09.15 12:00:00" to
                LocalDateTime.parse("2018.09.15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2018 Jul 15 12:00:00" to
                LocalDateTime.parse("2018 Jul 15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2021-1-1 01:01:01" to
                LocalDateTime.parse("2021-1-1 01:01:01", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2021.1.1 01:01:01" to
                LocalDateTime.parse("2021.1.1 01:01:01", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2021/1/1 01:01:01" to
                LocalDateTime.parse("2021/1/1 01:01:01", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2021-01-01 01:01:01" to
                LocalDateTime.parse("2021-01-01 01:01:01", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2021-1-1 01:01:01 +01" to
                ZonedDateTime.parse("2021-1-1 01:01:01 +01", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2018 Jul 15 12:00:00 GMT+08:00" to
                ZonedDateTime.parse("2018 Jul 15 12:00:00 GMT+08:00", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2018 Jul 15 12:00:00GMT+07" to
                ZonedDateTime.parse("2018 Jul 15 12:00:00GMT+07", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01+01:00" to
                ZonedDateTime.parse("2021-01-01T01:01:01+01:00", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01.546+01:00" to
                ZonedDateTime.parse("2021-01-01T01:01:01.546+01:00", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01 01:01:01 +0000" to
                ZonedDateTime.parse("2021-01-01 01:01:01 +0000", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021/01/01 01:01:01 +0000" to
                ZonedDateTime.parse("2021/01/01 01:01:01 +0000", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01Z" to
                ZonedDateTime.parse("2021-01-01T01:01:01Z", DATE_TIME_FORMATTER).toOffsetDateTime(),
            "2021-01-01T01:01:01-01:00" to
                ZonedDateTime.parse("2021-01-01T01:01:01-01:00", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01+01:00" to
                ZonedDateTime.parse("2021-01-01T01:01:01+01:00", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01 01:01:01 UTC" to
                ZonedDateTime.parse("2021-01-01 01:01:01 UTC", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01 PST" to
                ZonedDateTime.parse("2021-01-01T01:01:01 PST", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01 +0000" to
                ZonedDateTime.parse("2021-01-01T01:01:01 +0000", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01+0000" to
                ZonedDateTime.parse("2021-01-01T01:01:01+0000", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01UTC" to
                ZonedDateTime.parse("2021-01-01T01:01:01UTC", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01+01" to
                ZonedDateTime.parse("2021-01-01T01:01:01+01", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2022-01-23T01:23:45.678-11:30 BC" to
                ZonedDateTime.parse("2022-01-23T01:23:45.678-11:30 BC", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2022-01-23T01:23:45.678-11:30" to
                ZonedDateTime.parse("2022-01-23T01:23:45.678-11:30", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
        )

    @Test
    fun testCoerceTimestampWithTimezone() {
        timestampPairs.forEach { (input, offsetDateTime) ->
            val (value, changes) = mapper.map(StringValue(input), TimestampTypeWithTimezone)

            assertAll(
                "Failed for input $input",
                { assertEquals(TimestampWithTimezoneValue(offsetDateTime), value) },
                { assertEquals(emptyList<Meta.Change>(), changes) }
            )
        }
    }

    @Test
    fun testCoerceTimestampWithoutTimezone() {
        timestampPairs.forEach { (input, offsetDateTime) ->
            val (value, changes) = mapper.map(StringValue(input), TimestampTypeWithoutTimezone)

            assertAll(
                "Failed for input $input",
                {
                    assertEquals(
                        TimestampWithoutTimezoneValue(offsetDateTime.toLocalDateTime()),
                        value
                    )
                },
                { assertEquals(emptyList<Meta.Change>(), changes) }
            )
        }
    }

    private val timePairs: List<Pair<String, OffsetTime>> =
        listOf(
            "01:01:01" to LocalTime.parse("01:01:01").atOffset(ZoneOffset.UTC),
            "01:01" to LocalTime.parse("01:01").atOffset(ZoneOffset.UTC),
            "12:23:01.541" to LocalTime.parse("12:23:01.541").atOffset(ZoneOffset.UTC),
            "12:23:01.541214" to LocalTime.parse("12:23:01.541214").atOffset(ZoneOffset.UTC),
            "12:00:00.000000+01:00" to OffsetTime.parse("12:00:00.000000+01:00"),
            "10:00:00.000000-01:00" to OffsetTime.parse("10:00:00.000000-01:00"),
            "03:30:00.000000+04:00" to OffsetTime.parse("03:30:00.000000+04:00"),
        )

    @Test
    fun testCoerceTimeWithTimezone() {
        timePairs.forEach { (input, offsetTime) ->
            val (value, changes) = mapper.map(StringValue(input), TimeTypeWithTimezone)

            assertAll(
                "Failed for input $input",
                { assertEquals(TimeWithTimezoneValue(offsetTime), value) },
                { assertEquals(emptyList<Meta.Change>(), changes) }
            )
        }
    }

    @Test
    fun testCoerceTimeWithoutTimezone() {
        timePairs.forEach { (input, offsetTime) ->
            val (value, changes) = mapper.map(StringValue(input), TimeTypeWithoutTimezone)

            assertAll(
                "Failed for input $input",
                { assertEquals(TimeWithoutTimezoneValue(offsetTime.toLocalTime()), value) },
                { assertEquals(emptyList<Meta.Change>(), changes) }
            )
        }
    }

    @Test
    fun testCoerceNestedValue() {
        val (mappedValue, changes) =
            mapper.map(
                Jsons.readTree(
                        """
                    {
                        "sub_object": {
                            "undeclared": 42,
                            "timestamptz": "invalid"
                        },
                        "sub_array": ["invalid"]
                    }
                """.trimIndent()
                    )
                    .toAirbyteValue(),
                ObjectType(
                    linkedMapOf(
                        "sub_object" to
                            f(
                                ObjectType(
                                    linkedMapOf("timestamptz" to f(TimestampTypeWithTimezone))
                                )
                            ),
                        "sub_array" to f(ArrayType(f(IntegerType)))
                    )
                ),
            )
        assertAll(
            {
                assertEquals(
                    ObjectValue(
                        linkedMapOf(
                            "sub_object" to
                                ObjectValue(
                                    linkedMapOf(
                                        "undeclared" to IntegerValue(42),
                                        "timestamptz" to StringValue("invalid"),
                                    )
                                ),
                            "sub_array" to ArrayValue(listOf(StringValue("invalid")))
                        )
                    ),
                    mappedValue
                )
            },
            { assertEquals(emptyList<Meta.Change>(), changes) },
        )
    }

    /**
     * Identical to [testCoerceNestedValue], but uses a mapper with
     * [AirbyteValueDeepCoercingMapper.recurseIntoObjects] and
     * [AirbyteValueDeepCoercingMapper.recurseIntoArrays] enabled.
     */
    @Test
    fun testCoerceNestedValueRecursing() {
        val mapper =
            AirbyteValueDeepCoercingMapper(
                recurseIntoObjects = true,
                recurseIntoArrays = true,
                recurseIntoUnions = true,
            )
        val (mappedValue, changes) =
            mapper.map(
                Jsons.readTree(
                        """
                    {
                        "sub_object": {
                            "undeclared": 42,
                            "timestamptz": "invalid"
                        },
                        "sub_array": ["invalid"]
                    }
                """.trimIndent()
                    )
                    .toAirbyteValue(),
                ObjectType(
                    linkedMapOf(
                        "sub_object" to
                            f(
                                ObjectType(
                                    linkedMapOf("timestamptz" to f(TimestampTypeWithTimezone))
                                )
                            ),
                        "sub_array" to f(ArrayType(f(IntegerType)))
                    )
                ),
            )
        assertAll(
            // Note: undeclared field is gone, and we null the invalid timestamp
            {
                assertEquals(
                    ObjectValue(
                        linkedMapOf(
                            "sub_object" to ObjectValue(linkedMapOf("timestamptz" to NullValue)),
                            "sub_array" to ArrayValue(listOf(NullValue))
                        )
                    ),
                    mappedValue
                )
            },
            {
                assertEquals(
                    listOf(
                        Meta.Change(
                            "sub_object.timestamptz",
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                        ),
                        Meta.Change(
                            "sub_array.[0]",
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                        )
                    ),
                    changes
                )
            },
        )
    }

    private fun f(type: AirbyteType) = FieldType(type, nullable = true)
}
