/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import java.math.BigDecimal
import java.math.BigInteger
import java.sql.Date as SqlDate
import java.sql.Time as SqlTime
import java.sql.Timestamp as SqlTimestamp
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.util.Base64
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Integration tests verifying that encoding and decoding are inverse operations. These tests ensure
 * data integrity across the encode-decode cycle.
 */
class ProtobufEncoderDecoderRoundTripTest {

    private val encoder = AirbyteValueProtobufEncoder()
    private val decoder = AirbyteValueProtobufDecoder()

    private fun <T> testRoundTrip(value: T, schemaType: io.airbyte.cdk.data.AirbyteSchemaType) {
        testRoundTrip(value, value, schemaType)
    }

    private fun <T> testRoundTrip(
        value: T,
        expectedValue: T,
        schemaType: io.airbyte.cdk.data.AirbyteSchemaType
    ) {
        val encoded = encoder.encode(value, schemaType)
        val decoded = decoder.decode(encoded.build())
        assertEquals(expectedValue, decoded, "Round trip failed for value: $value")
    }

    @Test
    fun testNullRoundTrip() {
        val encoded = encoder.encode(null, LeafAirbyteSchemaType.STRING)
        val decoded = decoder.decode(encoded.build())
        assertEquals(null, decoded)
    }

    @Test
    fun testBooleanRoundTrip() {
        testRoundTrip(true, LeafAirbyteSchemaType.BOOLEAN)
        testRoundTrip(false, LeafAirbyteSchemaType.BOOLEAN)
    }

    @Test
    fun testStringRoundTrip() {
        testRoundTrip("", LeafAirbyteSchemaType.STRING)
        testRoundTrip("hello world", LeafAirbyteSchemaType.STRING)
        testRoundTrip("special chars: !@#$%^&*()", LeafAirbyteSchemaType.STRING)
        testRoundTrip("unicode: 你好 مرحبا 😀", LeafAirbyteSchemaType.STRING)
        testRoundTrip("line\nbreaks\tand\ttabs", LeafAirbyteSchemaType.STRING)
    }

    @Test
    fun testIntegerRoundTrip() {
        // Int values
        testRoundTrip(0, 0.toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(42, 42.toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(-42, (-42).toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(Int.MAX_VALUE, Int.MAX_VALUE.toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(Int.MIN_VALUE, Int.MIN_VALUE.toBigInteger(), LeafAirbyteSchemaType.INTEGER)

        // Long values
        testRoundTrip(0L, 0L.toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(123456789L, 123456789L.toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(-123456789L, (-123456789L).toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(Long.MAX_VALUE, Long.MAX_VALUE.toBigInteger(), LeafAirbyteSchemaType.INTEGER)
        testRoundTrip(Long.MIN_VALUE, Long.MIN_VALUE.toBigInteger(), LeafAirbyteSchemaType.INTEGER)

        // BigInteger values (note: decoded as BigInteger)
        val smallBigInt = BigInteger.valueOf(999L)
        val encoded1 = encoder.encode(smallBigInt, LeafAirbyteSchemaType.INTEGER)
        val decoded1 = decoder.decode(encoded1.build())
        assertEquals(smallBigInt, decoded1)

        val largeBigInt = BigInteger.valueOf(Long.MAX_VALUE).multiply(BigInteger.valueOf(2))
        val encoded2 = encoder.encode(largeBigInt, LeafAirbyteSchemaType.INTEGER)
        val decoded2 = decoder.decode(encoded2.build())
        assertEquals(largeBigInt, decoded2)

        val veryLargeBigInt = BigInteger.valueOf(10).pow(100)
        val encoded3 = encoder.encode(veryLargeBigInt, LeafAirbyteSchemaType.INTEGER)
        val decoded3 = decoder.decode(encoded3.build())
        assertEquals(veryLargeBigInt, decoded3)
    }

    @Test
    fun testNumberRoundTrip() {
        // Double values (note: decoded as BigDecimal)
        val doubleValues =
            listOf(0.0, 1.5, -1.5, 123.456, -999.999, Double.MAX_VALUE, -Double.MAX_VALUE)
        doubleValues.forEach { value ->
            val encoded = encoder.encode(value, LeafAirbyteSchemaType.NUMBER)
            val decoded = decoder.decode(encoded.build()) as BigDecimal
            assertEquals(BigDecimal.valueOf(value), decoded)
        }

        // Float values (note: decoded as BigDecimal via Double)
        val floatValues = listOf(0.0f, 1.5f, -1.5f, 123.456f)
        floatValues.forEach { value ->
            val encoded = encoder.encode(value, LeafAirbyteSchemaType.NUMBER)
            val decoded = decoder.decode(encoded.build()) as BigDecimal
            assertEquals(BigDecimal.valueOf(value.toDouble()), decoded)
        }

        // BigDecimal values
        val bigDecValues =
            listOf(
                BigDecimal.ZERO,
                BigDecimal.ONE,
                BigDecimal("-123.456"),
                BigDecimal("123456789.987654321"),
                BigDecimal("0.123456789012345678901234567890")
            )
        bigDecValues.forEach { value -> testRoundTrip(value, LeafAirbyteSchemaType.NUMBER) }
    }

    @Test
    fun testDateRoundTrip() {
        testRoundTrip(LocalDate.of(2025, 10, 6), LeafAirbyteSchemaType.DATE)
        testRoundTrip(LocalDate.ofEpochDay(0), LeafAirbyteSchemaType.DATE)
        testRoundTrip(LocalDate.of(1970, 1, 1), LeafAirbyteSchemaType.DATE)
        testRoundTrip(LocalDate.of(2000, 1, 1), LeafAirbyteSchemaType.DATE)
        testRoundTrip(LocalDate.of(2024, 2, 29), LeafAirbyteSchemaType.DATE) // Leap day
        testRoundTrip(LocalDate.of(9999, 12, 31), LeafAirbyteSchemaType.DATE)
        testRoundTrip(LocalDate.of(1, 1, 1), LeafAirbyteSchemaType.DATE)
        testRoundTrip(LocalDate.MIN, LeafAirbyteSchemaType.DATE)
        testRoundTrip(LocalDate.MAX, LeafAirbyteSchemaType.DATE)

        // Test SqlDate conversion
        val sqlDate = SqlDate.valueOf("2025-10-06")
        val encoded = encoder.encode(sqlDate, LeafAirbyteSchemaType.DATE)
        val decoded = decoder.decode(encoded.build())
        assertEquals(sqlDate.toLocalDate(), decoded)
    }

    @Test
    fun testTimeWithoutTimezoneRoundTrip() {
        testRoundTrip(LocalTime.MIDNIGHT, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        testRoundTrip(LocalTime.NOON, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        testRoundTrip(LocalTime.MAX, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        testRoundTrip(LocalTime.MIN, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        testRoundTrip(LocalTime.of(14, 30, 45), LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        testRoundTrip(
            LocalTime.of(14, 30, 45, 123456789),
            LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
        )
        testRoundTrip(LocalTime.of(0, 0, 0, 1), LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)

        // Test SqlTime conversion
        val sqlTime = SqlTime.valueOf("14:30:45")
        val encoded = encoder.encode(sqlTime, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        val decoded = decoder.decode(encoded.build())
        assertEquals(sqlTime.toLocalTime(), decoded)
    }

    @Test
    fun testTimeWithTimezoneRoundTrip() {
        // Various timezone offsets
        val offsets =
            listOf(
                ZoneOffset.UTC,
                ZoneOffset.ofHours(1),
                ZoneOffset.ofHours(-1),
                ZoneOffset.ofHours(5),
                ZoneOffset.ofHours(-8),
                ZoneOffset.ofHours(12),
                ZoneOffset.ofHours(-12),
                ZoneOffset.ofHoursMinutes(5, 30),
                ZoneOffset.ofHoursMinutes(-5, -45),
                ZoneOffset.ofHoursMinutesSeconds(1, 30, 30),
                ZoneOffset.MIN,
                ZoneOffset.MAX
            )

        offsets.forEach { offset ->
            testRoundTrip(
                OffsetTime.of(14, 30, 45, 0, offset),
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
            )
            testRoundTrip(OffsetTime.MIN, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
            testRoundTrip(OffsetTime.MAX, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
            testRoundTrip(
                OffsetTime.of(14, 30, 45, 123456789, offset),
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
            )
            testRoundTrip(
                OffsetTime.of(0, 0, 0, 0, offset),
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
            )
            testRoundTrip(
                OffsetTime.of(23, 59, 59, 999999999, offset),
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
            )
        }
    }

    @Test
    fun testTimestampWithoutTimezoneRoundTrip() {
        testRoundTrip(
            LocalDateTime.of(2025, 10, 6, 14, 30, 45),
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
        )
        testRoundTrip(
            LocalDateTime.of(2025, 10, 6, 14, 30, 45, 123456789),
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
        )
        testRoundTrip(
            LocalDateTime.of(1970, 1, 1, 0, 0, 0, 0),
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
        )
        testRoundTrip(
            LocalDateTime.of(2025, 10, 6, 0, 0, 0, 0),
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
        )
        testRoundTrip(
            LocalDateTime.of(2024, 2, 29, 12, 0, 0),
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
        )
        testRoundTrip(
            LocalDateTime.of(9999, 12, 31, 23, 59, 59, 999999999),
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
        )
        testRoundTrip(LocalDateTime.MIN, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        testRoundTrip(LocalDateTime.MAX, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)

        // Test SqlTimestamp conversion
        val sqlTimestamp = SqlTimestamp.valueOf("2025-10-06 14:30:45.123456789")
        val encoded = encoder.encode(sqlTimestamp, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        val decoded = decoder.decode(encoded.build())
        assertEquals(sqlTimestamp.toLocalDateTime(), decoded)
    }

    @Test
    fun testTimestampWithTimezoneRoundTrip() {
        // Various timezone offsets
        val offsets =
            listOf(
                ZoneOffset.UTC,
                ZoneOffset.ofHours(1),
                ZoneOffset.ofHours(-1),
                ZoneOffset.ofHours(5),
                ZoneOffset.ofHours(-8),
                ZoneOffset.ofHours(12),
                ZoneOffset.ofHours(-12),
                ZoneOffset.ofHoursMinutes(5, 30),
                ZoneOffset.ofHoursMinutes(-5, -45),
                ZoneOffset.ofHoursMinutes(-3, -30),
                ZoneOffset.ofHoursMinutes(-4, -30),
                ZoneOffset.ofHoursMinutes(9, 30),
                ZoneOffset.MIN,
                ZoneOffset.MAX
            )

        offsets.forEach { offset ->
            testRoundTrip(
                OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, offset),
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
            )
            testRoundTrip(OffsetDateTime.MIN, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
            testRoundTrip(OffsetDateTime.MAX, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
            testRoundTrip(
                OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 123456789, offset),
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
            )
            testRoundTrip(
                OffsetDateTime.of(1970, 1, 1, 0, 0, 0, 0, offset),
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
            )
        }

        // Test SqlTimestamp conversion (converts to UTC)
        val sqlTimestamp = SqlTimestamp.valueOf("2025-10-06 14:30:45.123456789")
        val encoded = encoder.encode(sqlTimestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        val decoded = decoder.decode(encoded.build()) as OffsetDateTime
        assertEquals(OffsetDateTime.ofInstant(sqlTimestamp.toInstant(), ZoneOffset.UTC), decoded)
    }

    @Test
    fun testJsonRoundTrip() {
        val jsonStrings =
            listOf(
                """{}""",
                """[]""",
                """{"key": "value"}""",
                """[1, 2, 3, "test"]""",
                """{"nested": {"object": true}}""",
                """{"unicode": "你好 مرحبا 😀"}"""
            )

        jsonStrings.forEach { json -> testRoundTrip(json, LeafAirbyteSchemaType.JSONB) }

        // Test with byte arrays
        jsonStrings.forEach { json ->
            val bytes = json.toByteArray()
            val encoded = encoder.encode(bytes, LeafAirbyteSchemaType.JSONB)
            val decoded = decoder.decode(encoded.build())
            assertEquals(json, decoded)
        }
    }

    @Test
    fun testBinaryRoundTrip() {
        val binaryStrings = listOf("simple text", "binary data with special chars: \n\t\r", "")

        binaryStrings.forEach { binary ->
            testRoundTrip(
                binary.toByteArray(),
                Base64.getEncoder().encodeToString(binary.toByteArray()),
                LeafAirbyteSchemaType.BINARY
            )
        }

        // Test with byte arrays
        val byteArrays =
            listOf(
                byteArrayOf(0x01, 0x02, 0x03),
                byteArrayOf(0xFF.toByte(), 0xFE.toByte()),
                byteArrayOf()
            )

        byteArrays.forEach { bytes ->
            val encoded = encoder.encode(bytes, LeafAirbyteSchemaType.BINARY)
            val decoded = decoder.decode(encoded.build()) as String
            assertEquals(Base64.getEncoder().encodeToString(bytes), decoded)
        }
    }

    @Test
    fun testComplexTimezoneScenarios() {
        // Test same instant in different timezones
        val baseTimestamp = OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, ZoneOffset.UTC)
        val timezones =
            listOf(
                ZoneOffset.ofHours(-8), // PST
                ZoneOffset.ofHours(5), // IST (approximately)
                ZoneOffset.ofHours(9), // JST
                ZoneOffset.ofHoursMinutes(-4, -30) // VET
            )

        timezones.forEach { offset ->
            val timestamp = baseTimestamp.withOffsetSameInstant(offset)
            val encoded = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
            val decoded = decoder.decode(encoded.build()) as OffsetDateTime

            // Should preserve the instant and the offset
            assertEquals(timestamp.toInstant(), decoded.toInstant())
            assertEquals(timestamp.offset, decoded.offset)
            assertEquals(timestamp, decoded)
        }
    }

    @Test
    fun testDstTransitions() {
        // Test timestamps around DST transitions
        val dstTestCases =
            listOf(
                // Spring forward
                OffsetDateTime.of(2025, 3, 9, 1, 59, 0, 0, ZoneOffset.ofHours(-8)),
                OffsetDateTime.of(2025, 3, 9, 3, 0, 0, 0, ZoneOffset.ofHours(-7)),
                // Fall back
                OffsetDateTime.of(2025, 11, 2, 1, 0, 0, 0, ZoneOffset.ofHours(-7)),
                OffsetDateTime.of(2025, 11, 2, 1, 0, 0, 0, ZoneOffset.ofHours(-8))
            )

        dstTestCases.forEach { timestamp ->
            testRoundTrip(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        }
    }

    @Test
    fun testBuilderReuse() {
        // Test that builder reuse works correctly
        val builder =
            io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()

        // Encode multiple different types with the same builder
        val encoded1 = encoder.encode(42, LeafAirbyteSchemaType.INTEGER, builder)
        val decoded1 = decoder.decode(encoded1.build())
        assertEquals(BigInteger.valueOf(42), decoded1)

        val encoded2 = encoder.encode("hello", LeafAirbyteSchemaType.STRING, builder)
        val decoded2 = decoder.decode(encoded2.build())
        assertEquals("hello", decoded2)

        val encoded3 =
            encoder.encode(LocalDate.of(2025, 10, 6), LeafAirbyteSchemaType.DATE, builder)
        val decoded3 = decoder.decode(encoded3.build())
        assertEquals(LocalDate.of(2025, 10, 6), decoded3)
    }

    @Test
    fun testEdgeCaseValues() {
        // Test zero values
        testRoundTrip(0.0.toBigDecimal(), LeafAirbyteSchemaType.NUMBER)
        testRoundTrip(LocalTime.MIDNIGHT, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)

        // Test maximum precision
        val maxPrecisionTime = LocalTime.of(23, 59, 59, 999999999)
        testRoundTrip(maxPrecisionTime, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)

        val maxPrecisionTimestamp = LocalDateTime.of(2025, 10, 6, 23, 59, 59, 999999999)
        testRoundTrip(maxPrecisionTimestamp, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)

        // Test empty strings and collections
        testRoundTrip("", LeafAirbyteSchemaType.STRING)
        testRoundTrip("{}", LeafAirbyteSchemaType.JSONB)
        testRoundTrip("[]", LeafAirbyteSchemaType.JSONB)
    }

    @Test
    fun testAllTimezonesRoundTrip() {
        // Test all common timezone offsets
        for (hours in -12..14) {
            for (minutes in listOf(0, 15, 30, 45)) {
                if (hours == 14 && minutes > 0) continue // Skip invalid offsets
                if (hours == -12 && minutes > 0) continue // Skip invalid offsets

                try {
                    val offset =
                        ZoneOffset.ofHoursMinutes(hours, if (hours >= 0) minutes else -minutes)
                    val time = OffsetTime.of(12, 0, 0, 0, offset)
                    testRoundTrip(time, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)

                    val timestamp = OffsetDateTime.of(2025, 10, 6, 12, 0, 0, 0, offset)
                    testRoundTrip(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
                } catch (e: Exception) {
                    // Skip invalid timezone offsets
                }
            }
        }
    }

    @Test
    fun testLeapYearRoundTrip() {
        val leapYears = listOf(2000, 2004, 2020, 2024)
        leapYears.forEach { year ->
            val leapDay = LocalDate.of(year, 2, 29)
            testRoundTrip(leapDay, LeafAirbyteSchemaType.DATE)

            val leapDayTimestamp = LocalDateTime.of(year, 2, 29, 12, 0, 0)
            testRoundTrip(leapDayTimestamp, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        }
    }
}
