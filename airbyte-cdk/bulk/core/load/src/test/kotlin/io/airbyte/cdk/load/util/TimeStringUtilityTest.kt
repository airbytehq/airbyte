/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import io.airbyte.cdk.load.data.AirbyteValueDeepCoercingMapper
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

internal class TimeStringUtilityTest {

    @Test
    fun testToLocalDate() {
        val localDateString = "2024-11-18"
        val localDate = TimeStringUtility.toLocalDate(localDateString)
        assertEquals(
            LocalDate.parse(localDateString, AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER),
            localDate
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
            LocalDateTime.parse(
                localDateTimeString,
                AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER
            ),
            localDateTime
        )
    }

    @Test
    fun testToOffsetWithTimezone() {
        val offsetWithTimezoneString = "12:34:56Z"
        val offsetWithTimezone = TimeStringUtility.toOffset(offsetWithTimezoneString)
        assertEquals(
            OffsetTime.parse(
                    offsetWithTimezoneString,
                    AirbyteValueDeepCoercingMapper.TIME_FORMATTER
                )
                .toLocalTime(),
            offsetWithTimezone
        )
    }

    @Test
    fun testToOffsetWithoutTimezone() {
        val offsetWithoutTimezoneString = "12:34:56"
        val offsetWithoutTimezone = TimeStringUtility.toOffset(offsetWithoutTimezoneString)
        assertEquals(
            LocalTime.parse(
                offsetWithoutTimezoneString,
                AirbyteValueDeepCoercingMapper.TIME_FORMATTER
            ),
            offsetWithoutTimezone
        )
    }

    @Test
    fun testToOffsetDateTimeWithTimezone() {
        val offsetWithTimezoneString = "2024-11-18T12:34:56Z"
        val offsetWithTimezone = TimeStringUtility.toOffsetDateTime(offsetWithTimezoneString)
        assertEquals(
            ZonedDateTime.parse(
                    offsetWithTimezoneString,
                    AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER
                )
                .toOffsetDateTime(),
            offsetWithTimezone
        )
    }

    @Test
    fun testToOffsetDateTimeWithoutTimezone() {
        val offsetWithoutTimezoneString = "2024-11-18T12:34:56"
        val offsetWithoutTimezone = TimeStringUtility.toOffsetDateTime(offsetWithoutTimezoneString)
        assertEquals(
            LocalDateTime.parse(
                    offsetWithoutTimezoneString,
                    AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER
                )
                .atOffset(ZoneOffset.UTC),
            offsetWithoutTimezone
        )
    }

    @Test
    fun testToOffsetDateTimeInvalidFormat() {
        val invalidDateTime = "invalid-datetime"
        assertThrows(java.time.format.DateTimeParseException::class.java) {
            TimeStringUtility.toOffsetDateTime(invalidDateTime)
        }
    }
}
