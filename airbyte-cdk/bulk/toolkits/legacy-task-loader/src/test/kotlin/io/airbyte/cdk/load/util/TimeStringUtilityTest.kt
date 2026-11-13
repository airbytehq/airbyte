/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import io.airbyte.cdk.load.data.AirbyteValueCoercer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

internal class TimeStringUtilityTest {

    @Test
    fun testToLocalDate() {
        val localDateString = "2024-11-18"
        val localDate = TimeStringUtility.toLocalDate(localDateString)
        assertEquals(
            LocalDate.parse(localDateString, AirbyteValueCoercer.DATE_TIME_FORMATTER),
            localDate,
        )
    }

    @Test
    fun testToLocalDateInvalidDateString() {
        val invalidDateStr = "invalid-date"
        assertThrows(java.time.format.DateTimeParseException::class.java) {
            TimeStringUtility.toLocalDate(invalidDateStr)
        }
    }

    @Test
    fun testToLocalDateTime() {
        val localDateTimeString = "2024-11-18T12:34:56Z"
        val localDateTime = TimeStringUtility.toLocalDateTime(localDateTimeString)
        assertEquals(
            LocalDateTime.parse(localDateTimeString, AirbyteValueCoercer.DATE_TIME_FORMATTER),
            localDateTime,
        )
    }

    @Test
    fun testToOffsetWithTimezone() {
        val offsetWithTimezoneString = "12:34:56Z"
        val offsetWithTimezone = TimeStringUtility.toOffset(offsetWithTimezoneString)
        assertEquals(
            OffsetTime.parse(offsetWithTimezoneString, AirbyteValueCoercer.TIME_FORMATTER)
                .toLocalTime(),
            offsetWithTimezone,
        )
    }

    @Test
    fun testToOffsetWithoutTimezone() {
        val offsetWithoutTimezoneString = "12:34:56"
        val offsetWithoutTimezone = TimeStringUtility.toOffset(offsetWithoutTimezoneString)
        assertEquals(
            LocalTime.parse(offsetWithoutTimezoneString, AirbyteValueCoercer.TIME_FORMATTER),
            offsetWithoutTimezone,
        )
    }

    @Test
    fun testToOffsetDateTimeWithTimezone() {
        val offsetWithTimezoneString = "2024-11-18T12:34:56Z"
        val offsetWithTimezone = TimeStringUtility.toOffsetDateTime(offsetWithTimezoneString)
        assertEquals(
            ZonedDateTime.parse(offsetWithTimezoneString, AirbyteValueCoercer.DATE_TIME_FORMATTER)
                .toOffsetDateTime(),
            offsetWithTimezone,
        )
    }

    @Test
    fun testToOffsetDateTimeWithoutTimezone() {
        val offsetWithoutTimezoneString = "2024-11-18T12:34:56"
        val offsetWithoutTimezone = TimeStringUtility.toOffsetDateTime(offsetWithoutTimezoneString)
        assertEquals(
            LocalDateTime.parse(
                    offsetWithoutTimezoneString,
                    AirbyteValueCoercer.DATE_TIME_FORMATTER,
                )
                .atOffset(ZoneOffset.UTC),
            offsetWithoutTimezone,
        )
    }

    @Test
    fun testToOffsetDateTimeInvalidFormat() {
        val invalidDateTime = "invalid-datetime"
        assertThrows(java.time.format.DateTimeParseException::class.java) {
            TimeStringUtility.toOffsetDateTime(invalidDateTime)
        }
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("shortFractionalTimestampArgs")
    fun testShortFractionalSecondsTimestamp(input: String, expected: OffsetDateTime) {
        assertEquals(expected, TimeStringUtility.toOffsetDateTime(input))
        assertEquals(expected.toLocalDateTime(), TimeStringUtility.toLocalDateTime(input))
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("shortFractionalTimeArgs")
    fun testShortFractionalSecondsTime(input: String, expected: LocalTime) {
        assertEquals(expected, TimeStringUtility.toOffset(input))
    }

    companion object {
        @JvmStatic
        fun shortFractionalTimestampArgs(): Stream<Arguments> =
            Stream.of(
                Arguments.of(
                    "2026-11-11T17:01:52.4Z",
                    OffsetDateTime.of(2026, 11, 11, 17, 1, 52, 400_000_000, ZoneOffset.UTC),
                ),
                Arguments.of(
                    "2026-11-11T17:01:52.65Z",
                    OffsetDateTime.of(2026, 11, 11, 17, 1, 52, 650_000_000, ZoneOffset.UTC),
                ),
                Arguments.of(
                    "2026-11-11T17:01:52.05",
                    OffsetDateTime.of(2026, 11, 11, 17, 1, 52, 50_000_000, ZoneOffset.UTC),
                ),
            )

        @JvmStatic
        fun shortFractionalTimeArgs(): Stream<Arguments> =
            Stream.of(
                Arguments.of("12:00:00.4Z", LocalTime.of(12, 0, 0, 400_000_000)),
                Arguments.of("12:00:00.65+01:00", LocalTime.of(12, 0, 0, 650_000_000)),
                Arguments.of("12:00:00.05", LocalTime.of(12, 0, 0, 50_000_000)),
            )
    }
}
