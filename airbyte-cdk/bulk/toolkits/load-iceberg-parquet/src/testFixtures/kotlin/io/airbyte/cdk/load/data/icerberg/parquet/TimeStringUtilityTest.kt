/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg.parquet

import io.airbyte.cdk.load.data.iceberg.parquet.TimeStringUtility
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class TimeStringUtilityTest {

    @Test
    fun `toLocalDate should parse a valid date string`() {
        val dateStr = "2024-12-16T00:00:00"
        val date = TimeStringUtility.toLocalDate(dateStr)
        assertEquals(LocalDate.of(2024, 12, 16), date)
    }

    @Test
    fun `toLocalDate should throw exception for invalid date string`() {
        val invalidDateStr = "invalid-date"
        assertThrows(java.time.format.DateTimeParseException::class.java) {
            TimeStringUtility.toLocalDate(invalidDateStr)
        }
    }

    @Test
    fun `toOffset should parse time with timezone`() {
        val timeStrWithOffset = "12:34:56+02:00"
        val localTime = TimeStringUtility.toOffset(timeStrWithOffset)
        assertEquals(LocalTime.of(12, 34, 56), localTime)
    }

    @Test
    fun `toOffset should parse time without timezone`() {
        val timeStrWithoutOffset = "12:34:56"
        val localTime = TimeStringUtility.toOffset(timeStrWithoutOffset)
        assertEquals(LocalTime.of(12, 34, 56), localTime)
    }

    @Test
    fun `toOffsetDateTime should parse datetime with timezone`() {
        val dateTimeWithTz = "2024-12-16T12:34:56-05:00"
        val odt = TimeStringUtility.toOffsetDateTime(dateTimeWithTz)
        assertEquals(OffsetDateTime.of(2024, 12, 16, 12, 34, 56, 0, ZoneOffset.of("-05:00")), odt)
    }

    @Test
    fun `toOffsetDateTime should parse datetime without timezone as UTC`() {
        val dateTimeWithoutTz = "2024-12-16T12:34:56"
        val odt = TimeStringUtility.toOffsetDateTime(dateTimeWithoutTz)
        assertEquals(
            OffsetDateTime.of(LocalDateTime.of(2024, 12, 16, 12, 34, 56), ZoneOffset.UTC),
            odt
        )
    }

    @Test
    fun `toOffsetDateTime should throw exception for invalid format`() {
        val invalidDateTime = "invalid-datetime"
        assertThrows(java.time.format.DateTimeParseException::class.java) {
            TimeStringUtility.toOffsetDateTime(invalidDateTime)
        }
    }
}
