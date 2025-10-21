/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol

import com.google.protobuf.NullValue
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.lang.IllegalStateException
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
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class AirbyteValueProtobufEncoderTest {

    private val encoder = AirbyteValueProtobufEncoder()

    @Test
    fun testEncodeNull() {
        val result = encoder.encode(null, LeafAirbyteSchemaType.STRING)
        assertEquals(NullValue.NULL_VALUE, result.`null`)
        assertEquals(AirbyteValueProtobuf.ValueCase.NULL, result.valueCase)
    }

    @Test
    fun testEncodeBoolean() {
        val trueResult = encoder.encode(true, LeafAirbyteSchemaType.BOOLEAN)
        assertEquals(true, trueResult.boolean)
        assertEquals(AirbyteValueProtobuf.ValueCase.BOOLEAN, trueResult.valueCase)

        val falseResult = encoder.encode(false, LeafAirbyteSchemaType.BOOLEAN)
        assertEquals(false, falseResult.boolean)
        assertEquals(AirbyteValueProtobuf.ValueCase.BOOLEAN, falseResult.valueCase)
    }

    @Test
    fun testEncodeBooleanInvalidType() {
        assertThrows(IllegalArgumentException::class.java) {
            encoder.encode("true", LeafAirbyteSchemaType.BOOLEAN)
        }
    }

    @Test
    fun testEncodeString() {
        val result = encoder.encode("hello world", LeafAirbyteSchemaType.STRING)
        assertEquals("hello world", result.string)
        assertEquals(AirbyteValueProtobuf.ValueCase.STRING, result.valueCase)

        val emptyResult = encoder.encode("", LeafAirbyteSchemaType.STRING)
        assertEquals("", emptyResult.string)
    }

    @Test
    fun testEncodeStringInvalidType() {
        assertThrows(IllegalArgumentException::class.java) {
            encoder.encode(123, LeafAirbyteSchemaType.STRING)
        }
    }

    @Test
    fun testEncodeIntegerLong() {
        val result = encoder.encode(123456789L, LeafAirbyteSchemaType.INTEGER)
        assertEquals(123456789L, result.integer)
        assertEquals(AirbyteValueProtobuf.ValueCase.INTEGER, result.valueCase)
    }

    @Test
    fun testEncodeIntegerInt() {
        val result = encoder.encode(42, LeafAirbyteSchemaType.INTEGER)
        assertEquals(42L, result.integer)
        assertEquals(AirbyteValueProtobuf.ValueCase.INTEGER, result.valueCase)
    }

    @Test
    fun testEncodeIntegerSmallBigInteger() {
        val smallBigInt = BigInteger.valueOf(9999L)
        val result = encoder.encode(smallBigInt, LeafAirbyteSchemaType.INTEGER)
        assertEquals(9999L, result.integer)
        assertEquals(AirbyteValueProtobuf.ValueCase.INTEGER, result.valueCase)
    }

    @Test
    fun testEncodeIntegerLargeBigInteger() {
        // BigInteger with more than 63 bits
        val largeBigInt = BigInteger.valueOf(Long.MAX_VALUE).multiply(BigInteger.valueOf(2))
        val result = encoder.encode(largeBigInt, LeafAirbyteSchemaType.INTEGER)
        assertEquals(largeBigInt.toString(), result.bigInteger)
        assertEquals(AirbyteValueProtobuf.ValueCase.BIG_INTEGER, result.valueCase)
    }

    @Test
    fun testEncodeIntegerNegative() {
        val result = encoder.encode(-12345L, LeafAirbyteSchemaType.INTEGER)
        assertEquals(-12345L, result.integer)
    }

    @Test
    fun testEncodeIntegerInvalidType() {
        assertThrows(IllegalStateException::class.java) {
            encoder.encode("123", LeafAirbyteSchemaType.INTEGER)
        }
    }

    @Test
    fun testEncodeNumberDouble() {
        val result = encoder.encode(123.456, LeafAirbyteSchemaType.NUMBER)
        assertEquals(123.456, result.number)
        assertEquals(AirbyteValueProtobuf.ValueCase.NUMBER, result.valueCase)
    }

    @Test
    fun testEncodeNumberFloat() {
        val float = 123.456f
        val result = encoder.encode(123.456f, LeafAirbyteSchemaType.NUMBER)
        assertEquals(AirbyteValueProtobuf.ValueCase.NUMBER, result.valueCase)
        assertEquals(float.toDouble(), result.number)
    }

    @Test
    fun testEncodeNumberBigDecimal() {
        val bigDec = BigDecimal("123456789.987654321")
        val result = encoder.encode(bigDec, LeafAirbyteSchemaType.NUMBER)
        assertEquals(bigDec.toString(), result.bigDecimal)
        assertEquals(AirbyteValueProtobuf.ValueCase.BIG_DECIMAL, result.valueCase)
    }

    @Test
    fun testEncodeNumberNegative() {
        val result = encoder.encode(-999.999, LeafAirbyteSchemaType.NUMBER)
        assertEquals(-999.999, result.number)
    }

    @Test
    fun testEncodeNumberInvalidType() {
        assertThrows(IllegalStateException::class.java) {
            encoder.encode("123.456", LeafAirbyteSchemaType.NUMBER)
        }
    }

    @Test
    fun testEncodeDateLocalDate() {
        val date = LocalDate.of(2025, 10, 6)
        val result = encoder.encode(date, LeafAirbyteSchemaType.DATE)
        assertEquals(date.toEpochDay(), result.date)
        assertEquals(AirbyteValueProtobuf.ValueCase.DATE, result.valueCase)
    }

    @Test
    fun testEncodeDateSqlDate() {
        val date = SqlDate.valueOf("2025-10-06")
        val result = encoder.encode(date, LeafAirbyteSchemaType.DATE)
        assertEquals(date.toLocalDate().toEpochDay(), result.date)
        assertEquals(AirbyteValueProtobuf.ValueCase.DATE, result.valueCase)
    }

    @Test
    fun testEncodeDateEpochStart() {
        val date = LocalDate.ofEpochDay(0)
        val result = encoder.encode(date, LeafAirbyteSchemaType.DATE)
        assertEquals(0, result.date)
    }

    @Test
    fun testEncodeDateInvalidType() {
        assertThrows(IllegalStateException::class.java) {
            encoder.encode("2025-10-06", LeafAirbyteSchemaType.DATE)
        }
    }

    @Test
    fun testEncodeTimeWithoutTimezoneLocalTime() {
        val time = LocalTime.of(14, 30, 45, 123456789)
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        assertEquals(time.toNanoOfDay(), result.timeWithoutTimezone)
        assertEquals(AirbyteValueProtobuf.ValueCase.TIME_WITHOUT_TIMEZONE, result.valueCase)
    }

    @Test
    fun testEncodeTimeWithoutTimezoneSqlTime() {
        val time = SqlTime.valueOf("14:30:45")
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        assertEquals(time.toLocalTime().toNanoOfDay(), result.timeWithoutTimezone)
    }

    @Test
    fun testEncodeTimeWithoutTimezoneMidnight() {
        val time = LocalTime.MIDNIGHT
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        assertEquals(0L, result.timeWithoutTimezone)
    }

    @Test
    fun testEncodeTimeWithoutTimezoneMaxTime() {
        val time = LocalTime.MAX
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        assertEquals(time.toNanoOfDay(), result.timeWithoutTimezone)
    }

    @Test
    fun testEncodeTimeWithoutTimezoneInvalidType() {
        assertThrows(IllegalStateException::class.java) {
            encoder.encode("14:30:45", LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        }
    }

    @Test
    fun testEncodeTimeWithTimezoneUTC() {
        val time = OffsetTime.of(14, 30, 45, 123456789, ZoneOffset.UTC)
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
        assertEquals(time.toLocalTime().toNanoOfDay(), result.timeWithTimezone.nanosOfDay)
        assertEquals(0, result.timeWithTimezone.offsetSeconds)
        assertEquals(AirbyteValueProtobuf.ValueCase.TIME_WITH_TIMEZONE, result.valueCase)
    }

    @Test
    fun testEncodeTimeWithTimezonePositiveOffset() {
        val time = OffsetTime.of(14, 30, 45, 0, ZoneOffset.ofHours(5))
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
        assertEquals(time.toLocalTime().toNanoOfDay(), result.timeWithTimezone.nanosOfDay)
        assertEquals(18000, result.timeWithTimezone.offsetSeconds) // 5 hours = 18000 seconds
    }

    @Test
    fun testEncodeTimeWithTimezoneNegativeOffset() {
        val time = OffsetTime.of(14, 30, 45, 0, ZoneOffset.ofHours(-8))
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
        assertEquals(time.toLocalTime().toNanoOfDay(), result.timeWithTimezone.nanosOfDay)
        assertEquals(-28800, result.timeWithTimezone.offsetSeconds) // -8 hours = -28800 seconds
    }

    @Test
    fun testEncodeTimeWithTimezoneFractionalOffset() {
        val time = OffsetTime.of(14, 30, 45, 0, ZoneOffset.ofHoursMinutes(5, 30))
        val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
        assertEquals(19800, result.timeWithTimezone.offsetSeconds) // 5.5 hours = 19800 seconds
    }

    @Test
    fun testEncodeTimeWithTimezoneInvalidType() {
        assertThrows(IllegalArgumentException::class.java) {
            encoder.encode(LocalTime.now(), LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
        }
    }

    @Test
    fun testEncodeTimestampWithoutTimezoneLocalDateTime() {
        val timestamp = LocalDateTime.of(2025, 10, 6, 14, 30, 45, 123456789)
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        assertEquals(
            timestamp.toLocalDate().toEpochDay(),
            result.timestampWithoutTimezone.dateDaysSinceEpoch
        )
        assertEquals(
            timestamp.toLocalTime().toNanoOfDay(),
            result.timestampWithoutTimezone.nanosOfDay
        )
        assertEquals(AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITHOUT_TIMEZONE, result.valueCase)
    }

    @Test
    fun testEncodeTimestampWithoutTimezoneSqlTimestamp() {
        val timestamp = SqlTimestamp.valueOf("2025-10-06 14:30:45.123456789")
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        val localDateTime = timestamp.toLocalDateTime()
        assertEquals(
            localDateTime.toLocalDate().toEpochDay(),
            result.timestampWithoutTimezone.dateDaysSinceEpoch
        )
        assertEquals(
            localDateTime.toLocalTime().toNanoOfDay(),
            result.timestampWithoutTimezone.nanosOfDay
        )
    }

    @Test
    fun testEncodeTimestampWithoutTimezoneEpochStart() {
        val timestamp = LocalDateTime.of(1970, 1, 1, 0, 0, 0, 0)
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        assertEquals(0, result.timestampWithoutTimezone.dateDaysSinceEpoch)
        assertEquals(0L, result.timestampWithoutTimezone.nanosOfDay)
    }

    @Test
    fun testEncodeTimestampWithoutTimezoneInvalidType() {
        assertThrows(IllegalStateException::class.java) {
            encoder.encode("2025-10-06T14:30:45", LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        }
    }

    @Test
    fun testEncodeTimestampWithTimezoneUTC() {
        val timestamp = OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 123456789, ZoneOffset.UTC)
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        val instant = timestamp.toInstant()
        assertEquals(instant.epochSecond, result.timestampWithTimezone.epochSecond)
        assertEquals(instant.nano, result.timestampWithTimezone.nano)
        assertEquals(0, result.timestampWithTimezone.offsetSeconds)
        assertEquals(AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITH_TIMEZONE, result.valueCase)
    }

    @Test
    fun testEncodeTimestampWithTimezonePositiveOffset() {
        val timestamp = OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, ZoneOffset.ofHours(5))
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        val instant = timestamp.toInstant()
        assertEquals(instant.epochSecond, result.timestampWithTimezone.epochSecond)
        assertEquals(instant.nano, result.timestampWithTimezone.nano)
        assertEquals(18000, result.timestampWithTimezone.offsetSeconds)
    }

    @Test
    fun testEncodeTimestampWithTimezoneNegativeOffset() {
        val timestamp = OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, ZoneOffset.ofHours(-8))
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        val instant = timestamp.toInstant()
        assertEquals(instant.epochSecond, result.timestampWithTimezone.epochSecond)
        assertEquals(-28800, result.timestampWithTimezone.offsetSeconds)
    }

    @Test
    fun testEncodeTimestampWithTimezoneFractionalOffset() {
        val timestamp =
            OffsetDateTime.of(2025, 10, 6, 14, 30, 45, 0, ZoneOffset.ofHoursMinutes(-4, -30))
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        assertEquals(-16200, result.timestampWithTimezone.offsetSeconds)
    }

    @Test
    fun testEncodeTimestampWithTimezoneSqlTimestamp() {
        val timestamp = SqlTimestamp.valueOf("2025-10-06 14:30:45.123456789")
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        // SqlTimestamp converts to UTC
        val instant = timestamp.toInstant()
        assertEquals(instant.epochSecond, result.timestampWithTimezone.epochSecond)
        assertEquals(instant.nano, result.timestampWithTimezone.nano)
        assertEquals(0, result.timestampWithTimezone.offsetSeconds) // UTC
    }

    @Test
    fun testEncodeTimestampWithTimezoneEpochStart() {
        val timestamp = OffsetDateTime.of(1970, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC)
        val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        assertEquals(0L, result.timestampWithTimezone.epochSecond)
        assertEquals(0, result.timestampWithTimezone.nano)
        assertEquals(0, result.timestampWithTimezone.offsetSeconds)
    }

    @Test
    fun testEncodeTimestampWithTimezoneInvalidType() {
        assertThrows(IllegalStateException::class.java) {
            encoder.encode("2025-10-06T14:30:45Z", LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
        }
    }

    @Test
    fun testEncodeJsonString() {
        val json = """{"key": "value"}"""
        val result = encoder.encode(json, LeafAirbyteSchemaType.JSONB)
        assertEquals(json, result.json.toStringUtf8())
        assertEquals(AirbyteValueProtobuf.ValueCase.JSON, result.valueCase)
    }

    @Test
    fun testEncodeJsonByteArray() {
        val jsonBytes = """{"key": "value"}""".toByteArray()
        val result = encoder.encode(jsonBytes, LeafAirbyteSchemaType.JSONB)
        assertEquals("""{"key": "value"}""", result.json.toStringUtf8())
    }

    @Test
    fun testEncodeJsonInvalidType() {
        assertThrows(IllegalStateException::class.java) {
            encoder.encode(123, LeafAirbyteSchemaType.JSONB)
        }
    }

    @Test
    fun testEncodeBinaryString() {
        val binary = "binary data".toByteArray()
        val result = encoder.encode(binary, LeafAirbyteSchemaType.BINARY)
        assertEquals(Base64.getEncoder().encodeToString(binary), result.string)
    }

    @Test
    fun testEncodeBinaryByteArray() {
        val binaryBytes = byteArrayOf(0x01, 0x02, 0x03)
        val result = encoder.encode(binaryBytes, LeafAirbyteSchemaType.BINARY)
        assertEquals(Base64.getEncoder().encodeToString(binaryBytes), result.string)
    }

    @Test
    fun testEncodeNullType() {
        val result = encoder.encode("anything", LeafAirbyteSchemaType.NULL)
        assertEquals(NullValue.NULL_VALUE, result.`null`)
    }

    @Test
    fun testEncodeWithBuilderReuse() {
        val builder = AirbyteValueProtobuf.newBuilder()

        val result1 = encoder.encode(42, LeafAirbyteSchemaType.INTEGER, builder)
        assertEquals(42L, result1.integer)

        val result2 = encoder.encode("hello", LeafAirbyteSchemaType.STRING, builder)
        assertEquals("hello", result2.string)

        // Verify builder was cleared between uses
        assertEquals(AirbyteValueProtobuf.ValueCase.STRING, result2.valueCase)
    }

    @Test
    fun testEncodeMultipleTimezones() {
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
            val result = encoder.encode(time, LeafAirbyteSchemaType.TIME_WITH_TIMEZONE)
            assertEquals(offset.totalSeconds, result.timeWithTimezone.offsetSeconds)
        }
    }

    @Test
    fun testEncodeTimestampWithMultipleTimezones() {
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
            val result = encoder.encode(timestamp, LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
            assertEquals(offset.totalSeconds, result.timestampWithTimezone.offsetSeconds)
        }
    }

    @Test
    fun testEncodeExtremeValues() {
        // Test extreme integer values
        val maxLong = encoder.encode(Long.MAX_VALUE, LeafAirbyteSchemaType.INTEGER)
        assertEquals(Long.MAX_VALUE, maxLong.integer)

        val minLong = encoder.encode(Long.MIN_VALUE, LeafAirbyteSchemaType.INTEGER)
        assertEquals(Long.MIN_VALUE, minLong.integer)

        // Test extreme double values
        val maxDouble = encoder.encode(Double.MAX_VALUE, LeafAirbyteSchemaType.NUMBER)
        assertEquals(Double.MAX_VALUE, maxDouble.number, 0.0)

        val minDouble = encoder.encode(-Double.MAX_VALUE, LeafAirbyteSchemaType.NUMBER)
        assertEquals(-Double.MAX_VALUE, minDouble.number, 0.0)

        // Test extreme dates
        val farFutureDate = LocalDate.of(9999, 12, 31)
        val futureDateResult = encoder.encode(farFutureDate, LeafAirbyteSchemaType.DATE)
        assertEquals(farFutureDate.toEpochDay(), futureDateResult.date)
    }

    @Test
    fun testEncodeNanosecondPrecision() {
        // Test nanosecond precision for time
        val preciseTime = LocalTime.of(12, 30, 45, 123456789)
        val timeResult = encoder.encode(preciseTime, LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE)
        assertEquals(preciseTime.toNanoOfDay(), timeResult.timeWithoutTimezone)

        // Test nanosecond precision for timestamp
        val preciseTimestamp = LocalDateTime.of(2025, 10, 6, 12, 30, 45, 987654321)
        val timestampResult =
            encoder.encode(preciseTimestamp, LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE)
        assertEquals(
            preciseTimestamp.toLocalTime().toNanoOfDay(),
            timestampResult.timestampWithoutTimezone.nanosOfDay
        )
    }
}
