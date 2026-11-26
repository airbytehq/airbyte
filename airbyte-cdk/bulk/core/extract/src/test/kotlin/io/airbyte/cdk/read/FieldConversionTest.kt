/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BigDecimalIntegerCodec
import io.airbyte.cdk.data.BinaryCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType.BINARY
import io.airbyte.cdk.data.LeafAirbyteSchemaType.BOOLEAN
import io.airbyte.cdk.data.LeafAirbyteSchemaType.DATE
import io.airbyte.cdk.data.LeafAirbyteSchemaType.INTEGER
import io.airbyte.cdk.data.LeafAirbyteSchemaType.JSONB
import io.airbyte.cdk.data.LeafAirbyteSchemaType.NUMBER
import io.airbyte.cdk.data.LeafAirbyteSchemaType.STRING
import io.airbyte.cdk.data.LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
import io.airbyte.cdk.data.LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
import io.airbyte.cdk.data.LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
import io.airbyte.cdk.data.LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.nio.ByteBuffer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class FieldConversionTest {

    /** Converting [value], read with [encoder] as a [from] value, to a [to] value. */
    data class TestCase<T>(
        val from: AirbyteSchemaType,
        val to: AirbyteSchemaType,
        val value: T?,
        val encoder: JsonEncoder<T>,
        /** The converted value. For [JSONB], the JSON it encodes. [FAILS] when it can't convert. */
        val expected: Any? = FAILS,
    ) {
        fun convert(): FieldValueEncoder<*>? =
            FieldConversion.of(from, to)!!.convert(FieldValueEncoder(value, encoder))

        /** For test naming. E.g. `INTEGER 456 -> STRING "456"`; values are shown as JSON. */
        override fun toString(): String {
            val input: String = FieldValueEncoder(value, encoder).encode().toString()
            val output: String =
                when (expected) {
                    FAILS -> ""
                    is String -> " \"$expected\""
                    else -> " $expected"
                }
            return "$from $input -> $to$output"
        }
    }

    data class Types(
        val from: AirbyteSchemaType,
        val to: AirbyteSchemaType,
    ) {
        override fun toString(): String = "$from -> $to"
    }

    @ParameterizedTest(name = "[{index}] {0}")
    @MethodSource("conversions")
    fun testConversion(case: TestCase<*>) {
        val converted: FieldValueEncoder<*>? = case.convert()
        Assertions.assertNotNull(converted, "can't convert $case")
        val actual: Any? = converted!!.fieldValue
        if (case.to == JSONB && actual != null) {
            Assertions.assertEquals(case.expected, Jsons.readTree(actual as String))
        } else {
            Assertions.assertEquals(case.expected, actual)
        }
    }

    @ParameterizedTest(name = "[{index}] {0} fails")
    @MethodSource("unconvertibleValues")
    fun testUnconvertibleValue(case: TestCase<*>) {
        Assertions.assertNull(case.convert())
    }

    @ParameterizedTest(name = "[{index}] {0} is supported")
    @MethodSource("supportedConversions")
    fun testSupportedConversion(types: Types) {
        Assertions.assertNotNull(FieldConversion.of(types.from, types.to))
    }

    @ParameterizedTest(name = "[{index}] {0} is unsupported")
    @MethodSource("unsupportedConversions")
    fun testUnsupportedConversion(types: Types) {
        Assertions.assertNull(FieldConversion.of(types.from, types.to))
    }

    @ParameterizedTest(name = "[{index}] source type \"{0}\" matches {1}")
    @MethodSource("matchingSourceTypes")
    fun testSourceTypeMatches(
        sourceTypeName: String,
        actual: AirbyteSchemaType,
    ) {
        Assertions.assertTrue(FieldConversion.sourceTypeMatches(sourceTypeName, actual))
    }

    @ParameterizedTest(name = "[{index}] source type \"{0}\" does not match {1}")
    @MethodSource("nonMatchingSourceTypes")
    fun testSourceTypeDoesNotMatch(
        sourceTypeName: String,
        actual: AirbyteSchemaType,
    ) {
        Assertions.assertFalse(FieldConversion.sourceTypeMatches(sourceTypeName, actual))
    }

    companion object {
        /** Marks a [TestCase] whose value can't be converted. */
        private val FAILS = Any()

        @JvmStatic
        fun conversions(): List<TestCase<*>> =
            listOf(
                // To string.
                TestCase(INTEGER, STRING, 456L, LongCodec, "456"),
                TestCase(
                    INTEGER,
                    STRING,
                    BigDecimal("123456789012345678901234567890"),
                    BigDecimalIntegerCodec,
                    "123456789012345678901234567890",
                ),
                TestCase(NUMBER, STRING, BigDecimal("1.50"), BigDecimalCodec, "1.50"),
                TestCase(NUMBER, STRING, 1.5, DoubleCodec, "1.5"),
                TestCase(NUMBER, STRING, 1e20, DoubleCodec, "100000000000000000000"),
                TestCase(NUMBER, STRING, Double.NaN, DoubleCodec, "NaN"),
                TestCase(BOOLEAN, STRING, true, BooleanCodec, "true"),
                TestCase(DATE, STRING, LocalDate.parse("2024-01-02"), LocalDateCodec, "2024-01-02"),
                TestCase(
                    TIMESTAMP_WITHOUT_TIMEZONE,
                    STRING,
                    LocalDateTime.parse("2024-01-02T03:04:05"),
                    LocalDateTimeCodec,
                    "2024-01-02T03:04:05.000000",
                ),
                TestCase(
                    TIMESTAMP_WITH_TIMEZONE,
                    STRING,
                    OffsetDateTime.parse("2024-01-02T03:04:05Z"),
                    OffsetDateTimeCodec,
                    "2024-01-02T03:04:05.000000Z",
                ),
                // To number.
                TestCase(INTEGER, NUMBER, 456L, LongCodec, BigDecimal(456)),
                // Temporal widening.
                TestCase(
                    DATE,
                    TIMESTAMP_WITHOUT_TIMEZONE,
                    LocalDate.parse("2024-01-02"),
                    LocalDateCodec,
                    LocalDateTime.parse("2024-01-02T00:00:00"),
                ),
                TestCase(
                    DATE,
                    TIMESTAMP_WITH_TIMEZONE,
                    LocalDate.parse("2024-01-02"),
                    LocalDateCodec,
                    OffsetDateTime.parse("2024-01-02T00:00:00Z"),
                ),
                TestCase(
                    TIMESTAMP_WITHOUT_TIMEZONE,
                    TIMESTAMP_WITH_TIMEZONE,
                    LocalDateTime.parse("2024-01-02T03:04:05"),
                    LocalDateTimeCodec,
                    OffsetDateTime.parse("2024-01-02T03:04:05Z"),
                ),
                TestCase(
                    TIME_WITHOUT_TIMEZONE,
                    TIME_WITH_TIMEZONE,
                    LocalTime.parse("03:04:05"),
                    LocalTimeCodec,
                    OffsetTime.of(LocalTime.parse("03:04:05"), ZoneOffset.UTC),
                ),
                // To JSON.
                TestCase(STRING, JSONB, "abc", TextCodec, Jsons.textNode("abc")),
                TestCase(INTEGER, JSONB, 456L, LongCodec, Jsons.readTree("456")),
                TestCase(
                    ArrayAirbyteSchemaType(INTEGER),
                    JSONB,
                    listOf(1L, 2L),
                    ArrayEncoder(LongCodec),
                    Jsons.readTree("[1,2]"),
                ),
                TestCase(
                    BINARY,
                    JSONB,
                    ByteBuffer.wrap(byteArrayOf(1, 2)),
                    BinaryCodec,
                    Jsons.textNode("AQI="),
                ),
                // Null stays null.
                TestCase(INTEGER, STRING, null, NullCodec, null),
                TestCase(INTEGER, JSONB, null, NullCodec, null),
            )

        /** A connector-specific encoder could emit any JSON for a column. */
        @JvmStatic
        fun unconvertibleValues(): List<TestCase<*>> =
            listOf(
                TestCase(INTEGER, NUMBER, "abc", TextCodec),
                TestCase(DATE, TIMESTAMP_WITHOUT_TIMEZONE, "not a date", TextCodec),
                TestCase(TIMESTAMP_WITHOUT_TIMEZONE, TIMESTAMP_WITH_TIMEZONE, true, BooleanCodec),
                TestCase(INTEGER, STRING, listOf(1L), ArrayEncoder(LongCodec)),
            )

        @JvmStatic
        fun supportedConversions(): List<Types> =
            listOf(
                Types(INTEGER, NUMBER),
                Types(INTEGER, STRING),
                Types(NUMBER, STRING),
                Types(BOOLEAN, STRING),
                Types(DATE, TIMESTAMP_WITHOUT_TIMEZONE),
                Types(DATE, TIMESTAMP_WITH_TIMEZONE),
                Types(DATE, STRING),
                Types(TIMESTAMP_WITHOUT_TIMEZONE, TIMESTAMP_WITH_TIMEZONE),
                Types(TIMESTAMP_WITHOUT_TIMEZONE, STRING),
                Types(TIMESTAMP_WITH_TIMEZONE, STRING),
                Types(TIME_WITHOUT_TIMEZONE, TIME_WITH_TIMEZONE),
                Types(TIME_WITHOUT_TIMEZONE, STRING),
                Types(TIME_WITH_TIMEZONE, STRING),
                Types(STRING, JSONB),
                Types(BINARY, JSONB),
                Types(INTEGER, JSONB),
                Types(ArrayAirbyteSchemaType(STRING), JSONB),
            )

        @JvmStatic
        fun unsupportedConversions(): List<Types> =
            listOf(
                Types(STRING, NUMBER),
                Types(STRING, INTEGER),
                Types(NUMBER, INTEGER),
                Types(BINARY, STRING),
                Types(INTEGER, BINARY),
                Types(TIMESTAMP_WITH_TIMEZONE, TIMESTAMP_WITHOUT_TIMEZONE),
                Types(JSONB, STRING),
                Types(JSONB, JSONB),
                Types(INTEGER, ArrayAirbyteSchemaType(INTEGER)),
                Types(LeafAirbyteSchemaType.NULL, JSONB),
            )

        @JvmStatic
        fun matchingSourceTypes(): List<Arguments> =
            listOf(
                Arguments.of("integer", INTEGER),
                Arguments.of("number", NUMBER),
                Arguments.of("boolean", BOOLEAN),
                Arguments.of("string", STRING),
                Arguments.of("string", BINARY),
                Arguments.of("date", DATE),
                Arguments.of("timestamp_without_timezone", TIMESTAMP_WITHOUT_TIMEZONE),
                Arguments.of("timestamp_with_timezone", TIMESTAMP_WITH_TIMEZONE),
                Arguments.of("time_without_timezone", TIME_WITHOUT_TIMEZONE),
                Arguments.of("time_with_timezone", TIME_WITH_TIMEZONE),
                Arguments.of("array", ArrayAirbyteSchemaType(INTEGER)),
                Arguments.of("array", ArrayAirbyteSchemaType(STRING)),
                Arguments.of("multi", JSONB),
                Arguments.of("object", JSONB),
                Arguments.of("unknown", JSONB),
            )

        @JvmStatic
        fun nonMatchingSourceTypes(): List<Arguments> =
            listOf(
                Arguments.of("integer", NUMBER),
                Arguments.of("number", INTEGER),
                Arguments.of("string", JSONB),
                Arguments.of("timestamp_with_timezone", TIMESTAMP_WITHOUT_TIMEZONE),
                Arguments.of("array", JSONB),
                Arguments.of("INTEGER", INTEGER),
                Arguments.of("bogus", STRING),
            )
    }
}
