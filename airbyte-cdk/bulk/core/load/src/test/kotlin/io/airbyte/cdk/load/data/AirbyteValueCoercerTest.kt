/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

// Test cases ported from legacy-task-loader's AirbyteValueDeepCoercingMapperTest.kt,
// adapted to call AirbyteValueCoercer.coerce() directly.

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.AirbyteValueCoercer.DATE_TIME_FORMATTER
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class AirbyteValueCoercerTest {

    // ==================== Timestamp with timezone ====================

    private val timestampPairs: List<Pair<String, OffsetDateTime>> =
        listOf(
            // ISO formats — no timezone (should assume UTC)
            "2018-09-15 12:00:00" to
                LocalDateTime.parse("2018-09-15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            "2018-09-15 12:00:00.006542" to
                LocalDateTime.parse("2018-09-15 12:00:00.006542", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            // Slash separators
            "2018/09/15 12:00:00" to
                LocalDateTime.parse("2018/09/15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            // Dot separators
            "2018.09.15 12:00:00" to
                LocalDateTime.parse("2018.09.15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            // Abbreviated month name
            "2018 Jul 15 12:00:00" to
                LocalDateTime.parse("2018 Jul 15 12:00:00", DATE_TIME_FORMATTER)
                    .atOffset(ZoneOffset.UTC),
            // Single-digit month/day
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
            // With timezone offset — various formats
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
            // Z suffix
            "2021-01-01T01:01:01Z" to
                ZonedDateTime.parse("2021-01-01T01:01:01Z", DATE_TIME_FORMATTER).toOffsetDateTime(),
            // Negative offsets
            "2021-01-01T01:01:01-01:00" to
                ZonedDateTime.parse("2021-01-01T01:01:01-01:00", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01+01:00" to
                ZonedDateTime.parse("2021-01-01T01:01:01+01:00", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            // Named timezones
            "2021-01-01 01:01:01 UTC" to
                ZonedDateTime.parse("2021-01-01 01:01:01 UTC", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01 PST" to
                ZonedDateTime.parse("2021-01-01T01:01:01 PST", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            // Compact offsets
            "2021-01-01T01:01:01 +0000" to
                ZonedDateTime.parse("2021-01-01T01:01:01 +0000", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2021-01-01T01:01:01+0000" to
                ZonedDateTime.parse("2021-01-01T01:01:01+0000", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            // Appended named timezone
            "2021-01-01T01:01:01UTC" to
                ZonedDateTime.parse("2021-01-01T01:01:01UTC", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            // Short offset
            "2021-01-01T01:01:01+01" to
                ZonedDateTime.parse("2021-01-01T01:01:01+01", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            // BC era
            "2022-01-23T01:23:45.678-11:30 BC" to
                ZonedDateTime.parse("2022-01-23T01:23:45.678-11:30 BC", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
            "2022-01-23T01:23:45.678-11:30" to
                ZonedDateTime.parse("2022-01-23T01:23:45.678-11:30", DATE_TIME_FORMATTER)
                    .toOffsetDateTime(),
        )

    @Test
    fun testCoerceTimestampWithTimezone() {
        timestampPairs.forEach { (input, expectedOdt) ->
            val result =
                AirbyteValueCoercer.coerce(
                    StringValue(input),
                    TimestampTypeWithTimezone,
                )
            assertEquals(
                TimestampWithTimezoneValue(expectedOdt),
                result,
                "Failed for input: $input"
            )
        }
    }

    @Test
    fun testCoerceTimestampWithoutTimezone() {
        timestampPairs.forEach { (input, expectedOdt) ->
            val result =
                AirbyteValueCoercer.coerce(
                    StringValue(input),
                    TimestampTypeWithoutTimezone,
                )
            assertEquals(
                TimestampWithoutTimezoneValue(expectedOdt.toLocalDateTime()),
                result,
                "Failed for input: $input"
            )
        }
    }

    // ==================== Time with/without timezone ====================

    private val timePairs: List<Pair<String, OffsetTime>> =
        listOf(
            // Bare times — no timezone, assumes UTC
            "01:01:01" to LocalTime.parse("01:01:01").atOffset(ZoneOffset.UTC),
            "01:01" to LocalTime.parse("01:01").atOffset(ZoneOffset.UTC),
            "12:23:01.541" to LocalTime.parse("12:23:01.541").atOffset(ZoneOffset.UTC),
            "12:23:01.541214" to LocalTime.parse("12:23:01.541214").atOffset(ZoneOffset.UTC),
            // With timezone offset
            "12:00:00.000000+01:00" to OffsetTime.parse("12:00:00.000000+01:00"),
            "10:00:00.000000-01:00" to OffsetTime.parse("10:00:00.000000-01:00"),
            "03:30:00.000000+04:00" to OffsetTime.parse("03:30:00.000000+04:00"),
        )

    @Test
    fun testCoerceTimeWithTimezone() {
        timePairs.forEach { (input, expectedOt) ->
            val result =
                AirbyteValueCoercer.coerce(
                    StringValue(input),
                    TimeTypeWithTimezone,
                )
            assertEquals(TimeWithTimezoneValue(expectedOt), result, "Failed for input: $input")
        }
    }

    @Test
    fun testCoerceTimeWithoutTimezone() {
        timePairs.forEach { (input, expectedOt) ->
            val result =
                AirbyteValueCoercer.coerce(
                    StringValue(input),
                    TimeTypeWithoutTimezone,
                )
            assertEquals(
                TimeWithoutTimezoneValue(expectedOt.toLocalTime()),
                result,
                "Failed for input: $input"
            )
        }
    }

    // ==================== Date ====================

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
            .forEach { input ->
                val expected = LocalDate.parse(input, DATE_TIME_FORMATTER)
                val result = AirbyteValueCoercer.coerce(StringValue(input), DateType)
                assertEquals(DateValue(expected), result, "Failed for input: $input")
            }
    }

    // ==================== Edge cases ====================

    @Test
    fun testCoerceNullValue() {
        assertEquals(NullValue, AirbyteValueCoercer.coerce(NullValue, TimestampTypeWithTimezone))
    }

    @Test
    fun testCoerceAlreadyTypedTimestamp() {
        val odt = OffsetDateTime.parse("2024-01-23T01:23:45Z")
        val value = TimestampWithTimezoneValue(odt)
        assertEquals(value, AirbyteValueCoercer.coerce(value, TimestampTypeWithTimezone))
    }

    @Test
    fun testCoerceAlreadyTypedTime() {
        val ot = OffsetTime.parse("01:23:45Z")
        val value = TimeWithTimezoneValue(ot)
        assertEquals(value, AirbyteValueCoercer.coerce(value, TimeTypeWithTimezone))
    }

    @Test
    fun testCoerceWrongTypeReturnsNull() {
        // IntegerValue can't be coerced to a timestamp
        assertNull(AirbyteValueCoercer.coerce(IntegerValue(12345), TimestampTypeWithTimezone))
    }

    @Test
    fun testCoerceInvalidStringReturnsNull() {
        assertNull(
            AirbyteValueCoercer.coerce(StringValue("not-a-timestamp"), TimestampTypeWithTimezone)
        )
    }
}
