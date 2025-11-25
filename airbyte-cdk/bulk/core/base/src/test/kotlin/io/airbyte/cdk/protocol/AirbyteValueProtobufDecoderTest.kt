/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol

import com.google.protobuf.ByteString
import com.google.protobuf.NullValue
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.LocalDateTime as ProtoLocalDateTime
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.OffsetDateTime as ProtoOffsetDateTime
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.OffsetTime as ProtoOffsetTime
import java.math.BigDecimal
import java.math.BigInteger
import java.nio.charset.StandardCharsets
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class AirbyteValueProtobufDecoderTest {

    private val decoder = AirbyteValueProtobufDecoder()

    @Test
    fun testDecodeNull() {
        val nullValue = AirbyteValueProtobuf.newBuilder().setNull(NullValue.NULL_VALUE).build()
        assertNull(decoder.decode(nullValue))
    }

    @Test
    fun testDecodeValueNotSet() {
        val emptyValue = AirbyteValueProtobuf.newBuilder().build()
        assertNull(decoder.decode(emptyValue))
    }

    @Test
    fun testDecodeBoolean() {
        val trueValue = AirbyteValueProtobuf.newBuilder().setBoolean(true).build()
        assertEquals(true, decoder.decode(trueValue))

        val falseValue = AirbyteValueProtobuf.newBuilder().setBoolean(false).build()
        assertEquals(false, decoder.decode(falseValue))
    }

    @Test
    fun testDecodeString() {
        val value = AirbyteValueProtobuf.newBuilder().setString("hello world").build()
        assertEquals("hello world", decoder.decode(value))

        val emptyValue = AirbyteValueProtobuf.newBuilder().setString("").build()
        assertEquals("", decoder.decode(emptyValue))
    }

    @Test
    fun testDecodeIntegerSmall() {
        val value = AirbyteValueProtobuf.newBuilder().setInteger(42L).build()
        val result = decoder.decode(value)
        assertEquals(BigInteger.valueOf(42L), result)
    }

    @Test
    fun testDecodeIntegerLarge() {
        val value = AirbyteValueProtobuf.newBuilder().setInteger(Long.MAX_VALUE).build()
        val result = decoder.decode(value)
        assertEquals(BigInteger.valueOf(Long.MAX_VALUE), result)
    }

    @Test
    fun testDecodeIntegerNegative() {
        val value = AirbyteValueProtobuf.newBuilder().setInteger(-12345L).build()
        val result = decoder.decode(value)
        assertEquals(BigInteger.valueOf(-12345L), result)
    }

    @Test
    fun testDecodeBigInteger() {
        val largeBigInt = BigInteger.valueOf(Long.MAX_VALUE).multiply(BigInteger.valueOf(2))
        val value = AirbyteValueProtobuf.newBuilder().setBigInteger(largeBigInt.toString()).build()
        val result = decoder.decode(value)
        assertEquals(largeBigInt, result)
    }

    @Test
    fun testDecodeBigIntegerVeryLarge() {
        val veryLargeBigInt = BigInteger.valueOf(10).pow(100)
        val value =
            AirbyteValueProtobuf.newBuilder().setBigInteger(veryLargeBigInt.toString()).build()
        val result = decoder.decode(value)
        assertEquals(veryLargeBigInt, result)
    }

    @Test
    fun testDecodeNumberDouble() {
        val value = AirbyteValueProtobuf.newBuilder().setNumber(123.456).build()
        val result = decoder.decode(value)
        assertEquals(BigDecimal.valueOf(123.456), result)
    }

    @Test
    fun testDecodeNumberNegative() {
        val value = AirbyteValueProtobuf.newBuilder().setNumber(-999.999).build()
        val result = decoder.decode(value)
        assertEquals(BigDecimal.valueOf(-999.999), result)
    }

    @Test
    fun testDecodeBigDecimal() {
        val bigDec = BigDecimal("123456789.987654321")
        val value = AirbyteValueProtobuf.newBuilder().setBigDecimal(bigDec.toString()).build()
        val result = decoder.decode(value)
        assertEquals(bigDec, result)
    }

    @Test
    fun testDecodeBigDecimalVeryPrecise() {
        val preciseDec = BigDecimal("0.123456789012345678901234567890")
        val value = AirbyteValueProtobuf.newBuilder().setBigDecimal(preciseDec.toString()).build()
        val result = decoder.decode(value)
        assertEquals(preciseDec, result)
    }

    @Test
    fun testDecodeDate() {
        val date = LocalDate.of(2025, 10, 6)
        val value = AirbyteValueProtobuf.newBuilder().setDate(date.toEpochDay()).build()
        val result = decoder.decode(value)
        assertEquals(date, result)
    }

    @Test
    fun testDecodeDateEpochStart() {
        val date = LocalDate.ofEpochDay(0)
        val value = AirbyteValueProtobuf.newBuilder().setDate(0).build()
        val result = decoder.decode(value)
        assertEquals(date, result)
    }

    @Test
    fun testDecodeDateFarFuture() {
        val date = LocalDate.of(9999, 12, 31)
        val value = AirbyteValueProtobuf.newBuilder().setDate(date.toEpochDay()).build()
        val result = decoder.decode(value)
        assertEquals(date, result)
    }

    @Test
    fun testDecodeTimeWithoutTimezone() {
        val time = LocalTime.of(14, 30, 45, 123456789)
        val value =
            AirbyteValueProtobuf.newBuilder().setTimeWithoutTimezone(time.toNanoOfDay()).build()
        val result = decoder.decode(value)
        assertEquals(time, result)
    }

    @Test
    fun testDecodeTimeWithoutTimezoneMidnight() {
        val time = LocalTime.MIDNIGHT
        val value = AirbyteValueProtobuf.newBuilder().setTimeWithoutTimezone(0L).build()
        val result = decoder.decode(value)
        assertEquals(time, result)
    }

    @Test
    fun testDecodeTimeWithoutTimezoneMaxTime() {
        val time = LocalTime.MAX
        val value =
            AirbyteValueProtobuf.newBuilder().setTimeWithoutTimezone(time.toNanoOfDay()).build()
        val result = decoder.decode(value)
        assertEquals(time, result)
    }

    @Test
    fun testDecodeTimeWithTimezoneUTC() {
        val time = OffsetTime.of(14, 30, 45, 123456789, ZoneOffset.UTC)
        val protoTime =
            ProtoOffsetTime.newBuilder()
                .setNanosOfDay(time.toLocalTime().toNanoOfDay())
                .setOffsetSeconds(0)
                .build()
        val value = AirbyteValueProtobuf.newBuilder().setTimeWithTimezone(protoTime).build()
        val result = decoder.decode(value) as OffsetTime
        assertEquals(time, result)
    }

    @Test
    fun testDecodeTimeWithTimezonePositiveOffset() {
        val time = OffsetTime.of(14, 30, 45, 0, ZoneOffset.ofHours(5))
        val protoTime =
            ProtoOffsetTime.newBuilder()
                .setNanosOfDay(time.toLocalTime().toNanoOfDay())
                .setOffsetSeconds(18000)
                .build()
        val value = AirbyteValueProtobuf.newBuilder().setTimeWithTimezone(protoTime).build()
        val result = decoder.decode(value) as OffsetTime
        assertEquals(time, result)
    }

    @Test
    fun testDecodeTimeWithTimezoneNegativeOffset() {
        val time = OffsetTime.of(14, 30, 45, 0, ZoneOffset.ofHours(-8))
        val protoTime =
            ProtoOffsetTime.newBuilder()
                .setNanosOfDay(time.toLocalTime().toNanoOfDay())
                .setOffsetSeconds(-28800)
                .build()
        val value = AirbyteValueProtobuf.newBuilder().setTimeWithTimezone(protoTime).build()
        val result = decoder.decode(value) as OffsetTime
        assertEquals(time, result)
    }

    @Test
    fun testDecodeTimeWithTimezoneFractionalOffset() {
        val time = OffsetTime.of(14, 30, 45, 0, ZoneOffset.ofHoursMinutes(5, 30))
        val protoTime =
            ProtoOffsetTime.newBuilder()
                .setNanosOfDay(time.toLocalTime().toNanoOfDay())
                .setOffsetSeconds(19800)
                .build()
        val value = AirbyteValueProtobuf.newBuilder().setTimeWithTimezone(protoTime).build()
        val result = decoder.decode(value) as OffsetTime
        assertEquals(time, result)
    }

    @Test
    fun testDecodeTimestampWithoutTimezone() {
        val timestamp = LocalDateTime.of(2025, 10, 6, 14, 30, 45, 123456789)
        val protoTimestamp =
            ProtoLocalDateTime.newBuilder()
                .setDateDaysSinceEpoch(timestamp.toLocalDate().toEpochDay())
                .setNanosOfDay(timestamp.toLocalTime().toNanoOfDay())
                .build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithoutTimezone(protoTimestamp).build()
        val result = decoder.decode(value)
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeTimestampWithoutTimezoneEpochStart() {
        val timestamp = LocalDateTime.of(1970, 1, 1, 0, 0, 0, 0)
        val protoTimestamp =
            ProtoLocalDateTime.newBuilder().setDateDaysSinceEpoch(0).setNanosOfDay(0L).build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithoutTimezone(protoTimestamp).build()
        val result = decoder.decode(value)
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeTimestampWithoutTimezoneMidnight() {
        val timestamp = LocalDateTime.of(2025, 10, 6, 0, 0, 0, 0)
        val protoTimestamp =
            ProtoLocalDateTime.newBuilder()
                .setDateDaysSinceEpoch(timestamp.toLocalDate().toEpochDay())
                .setNanosOfDay(0L)
                .build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithoutTimezone(protoTimestamp).build()
        val result = decoder.decode(value)
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeTimestampWithTimezoneUTC() {
        val timestamp = OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 123456789, ZoneOffset.UTC)
        val instant = timestamp.toInstant()
        val protoTimestamp =
            ProtoOffsetDateTime.newBuilder()
                .setEpochSecond(instant.epochSecond)
                .setNano(instant.nano)
                .setOffsetSeconds(0)
                .build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
        val result = decoder.decode(value) as OffsetDateTime
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeTimestampWithTimezonePositiveOffset() {
        val timestamp = OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, ZoneOffset.ofHours(5))
        val instant = timestamp.toInstant()
        val protoTimestamp =
            ProtoOffsetDateTime.newBuilder()
                .setEpochSecond(instant.epochSecond)
                .setNano(instant.nano)
                .setOffsetSeconds(18000)
                .build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
        val result = decoder.decode(value) as OffsetDateTime
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeTimestampWithTimezoneNegativeOffset() {
        val timestamp = OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, ZoneOffset.ofHours(-8))
        val instant = timestamp.toInstant()
        val protoTimestamp =
            ProtoOffsetDateTime.newBuilder()
                .setEpochSecond(instant.epochSecond)
                .setNano(instant.nano)
                .setOffsetSeconds(-28800)
                .build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
        val result = decoder.decode(value) as OffsetDateTime
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeTimestampWithTimezoneFractionalOffset() {
        val timestamp =
            OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, ZoneOffset.ofHoursMinutes(-4, -30))
        val instant = timestamp.toInstant()
        val protoTimestamp =
            ProtoOffsetDateTime.newBuilder()
                .setEpochSecond(instant.epochSecond)
                .setNano(instant.nano)
                .setOffsetSeconds(-16200)
                .build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
        val result = decoder.decode(value) as OffsetDateTime
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeTimestampWithTimezoneEpochStart() {
        val timestamp = OffsetDateTime.of(1970, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC)
        val protoTimestamp =
            ProtoOffsetDateTime.newBuilder()
                .setEpochSecond(0L)
                .setNano(0)
                .setOffsetSeconds(0)
                .build()
        val value =
            AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
        val result = decoder.decode(value) as OffsetDateTime
        assertEquals(timestamp, result)
    }

    @Test
    fun testDecodeJson() {
        val json = """{"key": "value"}"""
        val value =
            AirbyteValueProtobuf.newBuilder()
                .setJson(ByteString.copyFrom(json, StandardCharsets.UTF_8))
                .build()
        val result = decoder.decode(value)
        assertEquals(json, result)
    }

    @Test
    fun testDecodeJsonArray() {
        val json = """[1, 2, 3, "test"]"""
        val value =
            AirbyteValueProtobuf.newBuilder()
                .setJson(ByteString.copyFrom(json, StandardCharsets.UTF_8))
                .build()
        val result = decoder.decode(value)
        assertEquals(json, result)
    }

    @Test
    fun testDecodeJsonEmpty() {
        val json = "{}"
        val value =
            AirbyteValueProtobuf.newBuilder()
                .setJson(ByteString.copyFrom(json, StandardCharsets.UTF_8))
                .build()
        val result = decoder.decode(value)
        assertEquals(json, result)
    }

    @Test
    fun testDecodeMultipleTimezones() {
        val timezones =
            listOf(
                ZoneOffset.UTC,
                ZoneOffset.ofHours(1),
                ZoneOffset.ofHours(-1),
                ZoneOffset.ofHours(12),
                ZoneOffset.ofHours(-12),
                ZoneOffset.ofHoursMinutes(5, 30),
                ZoneOffset.ofHoursMinutes(-5, -45),
                ZoneOffset.ofHoursMinutesSeconds(1, 30, 30)
            )

        timezones.forEach { offset ->
            val time = OffsetTime.of(12, 0, 0, 0, offset)
            val protoTime =
                ProtoOffsetTime.newBuilder()
                    .setNanosOfDay(time.toLocalTime().toNanoOfDay())
                    .setOffsetSeconds(offset.totalSeconds)
                    .build()
            val value = AirbyteValueProtobuf.newBuilder().setTimeWithTimezone(protoTime).build()
            val result = decoder.decode(value) as OffsetTime
            assertEquals(time, result)
        }
    }

    @Test
    fun testDecodeTimestampWithMultipleTimezones() {
        val timezones =
            listOf(
                ZoneOffset.UTC,
                ZoneOffset.ofHours(5),
                ZoneOffset.ofHours(-8),
                ZoneOffset.ofHoursMinutes(9, 30),
                ZoneOffset.ofHoursMinutes(-3, -30)
            )

        timezones.forEach { offset ->
            val timestamp = OffsetDateTime.of(2025, 10, 6, 12, 0, 0, 0, offset)
            val instant = timestamp.toInstant()
            val protoTimestamp =
                ProtoOffsetDateTime.newBuilder()
                    .setEpochSecond(instant.epochSecond)
                    .setNano(instant.nano)
                    .setOffsetSeconds(offset.totalSeconds)
                    .build()
            val value =
                AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
            val result = decoder.decode(value) as OffsetDateTime
            assertEquals(timestamp, result)
        }
    }

    @Test
    fun testDecodeExtremeValues() {
        // Test extreme integer values
        val maxLong = AirbyteValueProtobuf.newBuilder().setInteger(Long.MAX_VALUE).build()
        assertEquals(BigInteger.valueOf(Long.MAX_VALUE), decoder.decode(maxLong))

        val minLong = AirbyteValueProtobuf.newBuilder().setInteger(Long.MIN_VALUE).build()
        assertEquals(BigInteger.valueOf(Long.MIN_VALUE), decoder.decode(minLong))

        // Test extreme double values
        val maxDouble = AirbyteValueProtobuf.newBuilder().setNumber(Double.MAX_VALUE).build()
        assertEquals(BigDecimal.valueOf(Double.MAX_VALUE), decoder.decode(maxDouble))

        val minDouble = AirbyteValueProtobuf.newBuilder().setNumber(-Double.MAX_VALUE).build()
        assertEquals(BigDecimal.valueOf(-Double.MAX_VALUE), decoder.decode(minDouble))
    }

    @Test
    fun testDecodeNanosecondPrecision() {
        // Test nanosecond precision for time
        val preciseTime = LocalTime.of(12, 30, 45, 123456789)
        val timeValue =
            AirbyteValueProtobuf.newBuilder()
                .setTimeWithoutTimezone(preciseTime.toNanoOfDay())
                .build()
        assertEquals(preciseTime, decoder.decode(timeValue))

        // Test nanosecond precision for timestamp
        val preciseTimestamp = LocalDateTime.of(2025, 10, 6, 12, 30, 45, 987654321)
        val protoTimestamp =
            ProtoLocalDateTime.newBuilder()
                .setDateDaysSinceEpoch(preciseTimestamp.toLocalDate().toEpochDay())
                .setNanosOfDay(preciseTimestamp.toLocalTime().toNanoOfDay())
                .build()
        val timestampValue =
            AirbyteValueProtobuf.newBuilder().setTimestampWithoutTimezone(protoTimestamp).build()
        assertEquals(preciseTimestamp, decoder.decode(timestampValue))
    }

    @Test
    fun testDecodeSpecialDoubleValues() {
        val zero = AirbyteValueProtobuf.newBuilder().setNumber(0.0).build()
        assertEquals(0.0.toBigDecimal(), decoder.decode(zero))

        val negativeZero = AirbyteValueProtobuf.newBuilder().setNumber(-0.0).build()
        assertEquals(0.0.toBigDecimal(), decoder.decode(negativeZero))
    }

    @Test
    fun testDecodeUtf8Json() {
        val jsonWithUnicode = """{"emoji": "😀", "chinese": "你好", "arabic": "مرحبا"}"""
        val value =
            AirbyteValueProtobuf.newBuilder()
                .setJson(ByteString.copyFrom(jsonWithUnicode, StandardCharsets.UTF_8))
                .build()
        val result = decoder.decode(value)
        assertEquals(jsonWithUnicode, result)
    }

    @Test
    fun testDecodeAllTimezoneOffsets() {
        // Test various timezone offsets including edge cases
        val offsets =
            listOf(
                ZoneOffset.MIN, // -18:00
                ZoneOffset.MAX, // +18:00
                ZoneOffset.UTC, // +00:00
                ZoneOffset.ofHours(0),
                ZoneOffset.ofHoursMinutes(14, 0), // Kiribati
                ZoneOffset.ofHoursMinutes(-11, 0), // American Samoa
                ZoneOffset.ofHoursMinutes(5, 45), // Nepal
                ZoneOffset.ofHoursMinutes(12, 45), // Chatham Islands
                ZoneOffset.ofHoursMinutes(-3, -30), // Newfoundland
            )

        offsets.forEach { offset ->
            val timestamp = OffsetDateTime.of(2025, 6, 15, 12, 0, 0, 0, offset)
            val instant = timestamp.toInstant()
            val protoTimestamp =
                ProtoOffsetDateTime.newBuilder()
                    .setEpochSecond(instant.epochSecond)
                    .setNano(instant.nano)
                    .setOffsetSeconds(offset.totalSeconds)
                    .build()
            val value =
                AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
            val result = decoder.decode(value) as OffsetDateTime
            assertEquals(timestamp, result)
            assertEquals(offset, result.offset)
        }
    }

    @Test
    fun testDecodeTimeAcrossDaylightSavingTransitions() {
        // Test times around DST transitions with various offsets
        val testCases =
            listOf(
                // Spring forward scenarios
                Triple(
                    LocalDateTime.of(2025, 3, 9, 2, 30),
                    ZoneOffset.ofHours(-8),
                    "PST before spring forward"
                ),
                Triple(
                    LocalDateTime.of(2025, 3, 9, 3, 30),
                    ZoneOffset.ofHours(-7),
                    "PDT after spring forward"
                ),
                // Fall back scenarios
                Triple(
                    LocalDateTime.of(2025, 11, 2, 1, 30),
                    ZoneOffset.ofHours(-7),
                    "PDT before fall back"
                ),
                Triple(
                    LocalDateTime.of(2025, 11, 2, 1, 30),
                    ZoneOffset.ofHours(-8),
                    "PST after fall back"
                )
            )

        testCases.forEach { (localDateTime, offset, description) ->
            val timestamp = OffsetDateTime.of(localDateTime, offset)
            val instant = timestamp.toInstant()
            val protoTimestamp =
                ProtoOffsetDateTime.newBuilder()
                    .setEpochSecond(instant.epochSecond)
                    .setNano(instant.nano)
                    .setOffsetSeconds(offset.totalSeconds)
                    .build()
            val value =
                AirbyteValueProtobuf.newBuilder().setTimestampWithTimezone(protoTimestamp).build()
            val result = decoder.decode(value) as OffsetDateTime
            assertEquals(timestamp, result, "Failed for: $description")
        }
    }

    @Test
    fun testDecodeLeapYearDates() {
        // Test leap year dates
        val leapYearDates =
            listOf(
                LocalDate.of(2024, 2, 29), // Leap day 2024
                LocalDate.of(2000, 2, 29), // Leap day 2000 (divisible by 400)
                LocalDate.of(2020, 2, 29) // Leap day 2020
            )

        leapYearDates.forEach { date ->
            val value = AirbyteValueProtobuf.newBuilder().setDate(date.toEpochDay()).build()
            val result = decoder.decode(value)
            assertEquals(date, result)
        }
    }

    @Test
    fun testDecodeBoundaryDates() {
        // Test boundary dates
        val boundaryDates =
            listOf(
                LocalDate.of(1970, 1, 1), // Unix epoch
                LocalDate.of(1, 1, 1), // Year 1
                LocalDate.of(9999, 12, 31), // Max date
                LocalDate.of(2000, 1, 1), // Y2K
                LocalDate.of(1900, 2, 28), // Not a leap year (divisible by 100 but not 400)
                LocalDate.of(2100, 2, 28) // Not a leap year
            )

        boundaryDates.forEach { date ->
            val value = AirbyteValueProtobuf.newBuilder().setDate(date.toEpochDay()).build()
            val result = decoder.decode(value)
            assertEquals(date, result)
        }
    }
}
