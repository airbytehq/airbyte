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
import org.junit.jupiter.api.Test

class FieldConversionTest {

    private fun conversion(
        from: AirbyteSchemaType,
        to: AirbyteSchemaType,
    ): FieldConversion =
        FieldConversion.of(from, to) ?: throw AssertionError("expected a conversion $from -> $to")

    private fun <T> convert(
        from: AirbyteSchemaType,
        to: AirbyteSchemaType,
        value: T,
        encoder: JsonEncoder<T>,
    ): Any? {
        val converted: FieldValueEncoder<*>? =
            conversion(from, to).convert(FieldValueEncoder(value, encoder))
        Assertions.assertNotNull(converted, "can't convert $value from $from to $to")
        return converted!!.fieldValue
    }

    @Test
    fun testToString() {
        Assertions.assertEquals("456", convert(INTEGER, STRING, 456L, LongCodec))
        Assertions.assertEquals(
            "123456789012345678901234567890",
            convert(
                INTEGER,
                STRING,
                BigDecimal("123456789012345678901234567890"),
                BigDecimalIntegerCodec,
            ),
        )
        Assertions.assertEquals(
            "1.50",
            convert(NUMBER, STRING, BigDecimal("1.50"), BigDecimalCodec),
        )
        Assertions.assertEquals("1.5", convert(NUMBER, STRING, 1.5, DoubleCodec))
        Assertions.assertEquals(
            "100000000000000000000",
            convert(NUMBER, STRING, 1e20, DoubleCodec),
        )
        Assertions.assertEquals("NaN", convert(NUMBER, STRING, Double.NaN, DoubleCodec))
        Assertions.assertEquals("true", convert(BOOLEAN, STRING, true, BooleanCodec))
        Assertions.assertEquals(
            "2024-01-02",
            convert(DATE, STRING, LocalDate.parse("2024-01-02"), LocalDateCodec),
        )
        Assertions.assertEquals(
            "2024-01-02T03:04:05.000000",
            convert(
                TIMESTAMP_WITHOUT_TIMEZONE,
                STRING,
                LocalDateTime.parse("2024-01-02T03:04:05"),
                LocalDateTimeCodec,
            ),
        )
        Assertions.assertEquals(
            "2024-01-02T03:04:05.000000Z",
            convert(
                TIMESTAMP_WITH_TIMEZONE,
                STRING,
                OffsetDateTime.parse("2024-01-02T03:04:05Z"),
                OffsetDateTimeCodec,
            ),
        )
    }

    @Test
    fun testIntegerToNumber() {
        Assertions.assertEquals(BigDecimal(456), convert(INTEGER, NUMBER, 456L, LongCodec))
    }

    @Test
    fun testTemporalWidening() {
        Assertions.assertEquals(
            LocalDateTime.parse("2024-01-02T00:00:00"),
            convert(
                DATE,
                TIMESTAMP_WITHOUT_TIMEZONE,
                LocalDate.parse("2024-01-02"),
                LocalDateCodec,
            ),
        )
        Assertions.assertEquals(
            OffsetDateTime.parse("2024-01-02T00:00:00Z"),
            convert(DATE, TIMESTAMP_WITH_TIMEZONE, LocalDate.parse("2024-01-02"), LocalDateCodec),
        )
        Assertions.assertEquals(
            OffsetDateTime.parse("2024-01-02T03:04:05Z"),
            convert(
                TIMESTAMP_WITHOUT_TIMEZONE,
                TIMESTAMP_WITH_TIMEZONE,
                LocalDateTime.parse("2024-01-02T03:04:05"),
                LocalDateTimeCodec,
            ),
        )
        Assertions.assertEquals(
            OffsetTime.of(LocalTime.parse("03:04:05"), ZoneOffset.UTC),
            convert(
                TIME_WITHOUT_TIMEZONE,
                TIME_WITH_TIMEZONE,
                LocalTime.parse("03:04:05"),
                LocalTimeCodec,
            ),
        )
    }

    @Test
    fun testToJson() {
        fun <T> json(
            from: AirbyteSchemaType,
            value: T,
            encoder: JsonEncoder<T>,
        ) = Jsons.readTree(convert(from, JSONB, value, encoder) as String)
        Assertions.assertEquals(Jsons.textNode("abc"), json(STRING, "abc", TextCodec))
        Assertions.assertEquals(Jsons.readTree("456"), json(INTEGER, 456L, LongCodec))
        Assertions.assertEquals(
            Jsons.readTree("[1,2]"),
            json(ArrayAirbyteSchemaType(INTEGER), listOf(1L, 2L), ArrayEncoder(LongCodec)),
        )
        Assertions.assertEquals(
            Jsons.textNode("AQI="),
            json(BINARY, ByteBuffer.wrap(byteArrayOf(1, 2)), BinaryCodec),
        )
    }

    @Test
    fun testNull() {
        val converted: FieldValueEncoder<*>? =
            conversion(INTEGER, STRING).convert(FieldValueEncoder(null, NullCodec))
        Assertions.assertNotNull(converted)
        Assertions.assertNull(converted!!.fieldValue)
    }

    @Test
    fun testUnconvertibleValue() {
        // A connector-specific encoder could emit any JSON for an integer column.
        Assertions.assertNull(
            conversion(INTEGER, NUMBER).convert(FieldValueEncoder("abc", TextCodec)),
        )
    }

    @Test
    fun testSupportedConversions() {
        val supported: List<Pair<AirbyteSchemaType, AirbyteSchemaType>> =
            listOf(
                INTEGER to NUMBER,
                INTEGER to STRING,
                NUMBER to STRING,
                BOOLEAN to STRING,
                DATE to TIMESTAMP_WITHOUT_TIMEZONE,
                DATE to TIMESTAMP_WITH_TIMEZONE,
                DATE to STRING,
                TIMESTAMP_WITHOUT_TIMEZONE to TIMESTAMP_WITH_TIMEZONE,
                TIMESTAMP_WITHOUT_TIMEZONE to STRING,
                TIMESTAMP_WITH_TIMEZONE to STRING,
                TIME_WITHOUT_TIMEZONE to TIME_WITH_TIMEZONE,
                TIME_WITHOUT_TIMEZONE to STRING,
                TIME_WITH_TIMEZONE to STRING,
                STRING to JSONB,
                BINARY to JSONB,
                INTEGER to JSONB,
                ArrayAirbyteSchemaType(STRING) to JSONB,
            )
        for ((from, to) in supported) {
            Assertions.assertNotNull(FieldConversion.of(from, to), "$from -> $to")
        }
        val unsupported: List<Pair<AirbyteSchemaType, AirbyteSchemaType>> =
            listOf(
                STRING to NUMBER,
                STRING to INTEGER,
                NUMBER to INTEGER,
                BINARY to STRING,
                INTEGER to BINARY,
                TIMESTAMP_WITH_TIMEZONE to TIMESTAMP_WITHOUT_TIMEZONE,
                JSONB to STRING,
                JSONB to JSONB,
                INTEGER to ArrayAirbyteSchemaType(INTEGER),
                LeafAirbyteSchemaType.NULL to JSONB,
            )
        for ((from, to) in unsupported) {
            Assertions.assertNull(FieldConversion.of(from, to), "$from -> $to")
        }
    }

    @Test
    fun testSourceTypeMatches() {
        val matching: List<Pair<String, AirbyteSchemaType>> =
            listOf(
                "integer" to INTEGER,
                "number" to NUMBER,
                "boolean" to BOOLEAN,
                "string" to STRING,
                "string" to BINARY,
                "date" to DATE,
                "timestamp_without_timezone" to TIMESTAMP_WITHOUT_TIMEZONE,
                "timestamp_with_timezone" to TIMESTAMP_WITH_TIMEZONE,
                "time_without_timezone" to TIME_WITHOUT_TIMEZONE,
                "time_with_timezone" to TIME_WITH_TIMEZONE,
                "array" to ArrayAirbyteSchemaType(INTEGER),
                "array" to ArrayAirbyteSchemaType(STRING),
                "multi" to JSONB,
                "object" to JSONB,
                "unknown" to JSONB,
            )
        for ((name, type) in matching) {
            Assertions.assertTrue(FieldConversion.sourceTypeMatches(name, type), "$name ~ $type")
        }
        val notMatching: List<Pair<String, AirbyteSchemaType>> =
            listOf(
                "integer" to NUMBER,
                "number" to INTEGER,
                "string" to JSONB,
                "timestamp_with_timezone" to TIMESTAMP_WITHOUT_TIMEZONE,
                "array" to JSONB,
                "INTEGER" to INTEGER,
                "bogus" to STRING,
            )
        for ((name, type) in notMatching) {
            Assertions.assertFalse(FieldConversion.sourceTypeMatches(name, type), "$name ~ $type")
        }
    }
}
