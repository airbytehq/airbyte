/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import java.sql.ResultSet
import java.sql.Timestamp
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class SnowflakeFieldTypesTest {

    // --- SnowflakeLocalDateTimeAccessor tests ---

    @Test
    fun `SnowflakeLocalDateTimeAccessor rounds up 9 decimal places to 6`() {
        val dateTimeWith9Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456789)
        val timestamp = Timestamp.valueOf(dateTimeWith9Decimals)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeLocalDateTimeAccessor.get(rs, 1)

        val expected = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123457000)
        assertEquals(expected, result)
    }

    @Test
    fun `SnowflakeLocalDateTimeAccessor rounding up never produces a value less than the original`() {
        val dateTimeWith9Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456789)
        val timestamp = Timestamp.valueOf(dateTimeWith9Decimals)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeLocalDateTimeAccessor.get(rs, 1)

        assertTrue(result!! >= dateTimeWith9Decimals)
    }

    @Test
    fun `SnowflakeLocalDateTimeAccessor rounding up carries into the next second`() {
        val dateTimeNearSecondBoundary = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 999999999)
        val timestamp = Timestamp.valueOf(dateTimeNearSecondBoundary)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeLocalDateTimeAccessor.get(rs, 1)

        val expected = LocalDateTime.of(2025, 11, 6, 22, 30, 47, 0)
        assertEquals(expected, result)
    }

    @Test
    fun `SnowflakeLocalDateTimeAccessor preserves datetime with exactly 6 decimal places`() {
        val dateTimeWith6Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456000)
        val timestamp = Timestamp.valueOf(dateTimeWith6Decimals)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeLocalDateTimeAccessor.get(rs, 1)

        assertEquals(dateTimeWith6Decimals, result)
    }

    @Test
    fun `SnowflakeLocalDateTimeAccessor preserves datetime with fewer than 6 decimal places`() {
        val dateTimeWith3Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123000000)
        val timestamp = Timestamp.valueOf(dateTimeWith3Decimals)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeLocalDateTimeAccessor.get(rs, 1)

        assertEquals(dateTimeWith3Decimals, result)
    }

    @Test
    fun `SnowflakeLocalDateTimeAccessor returns null for null timestamp`() {
        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(null)
        `when`(rs.wasNull()).thenReturn(true)

        val result = SnowflakeLocalDateTimeAccessor.get(rs, 1)

        assertNull(result)
    }

    // --- SnowflakeOffsetDateTimeFieldType tests ---

    @Test
    fun `SnowflakeOffsetDateTimeFieldType rounds up 9 decimal places to 6`() {
        val dateTimeWith9Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456789)
        val timestamp = Timestamp.valueOf(dateTimeWith9Decimals)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeOffsetDateTimeFieldType.jdbcGetter.get(rs, 1)

        val expected = OffsetDateTime.of(2025, 11, 6, 22, 30, 46, 123457000, ZoneOffset.UTC)
        assertEquals(expected, result)
        assertEquals(123457000, result?.nano)
    }

    @Test
    fun `SnowflakeOffsetDateTimeFieldType preserves datetime with exactly 6 decimal places`() {
        val dateTimeWith6Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456000)
        val timestamp = Timestamp.valueOf(dateTimeWith6Decimals)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeOffsetDateTimeFieldType.jdbcGetter.get(rs, 1)

        val expected = OffsetDateTime.of(2025, 11, 6, 22, 30, 46, 123456000, ZoneOffset.UTC)
        assertEquals(expected, result)
    }

    @Test
    fun `SnowflakeOffsetDateTimeFieldType returns null for null timestamp`() {
        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(null)
        `when`(rs.wasNull()).thenReturn(true)

        val result = SnowflakeOffsetDateTimeFieldType.jdbcGetter.get(rs, 1)

        assertNull(result)
    }

    @Test
    fun `SnowflakeOffsetDateTimeFieldType converts to UTC offset`() {
        val localDateTime = LocalDateTime.of(2025, 6, 15, 10, 0, 0, 500000123)
        val timestamp = Timestamp.valueOf(localDateTime)

        val rs = mock(ResultSet::class.java)
        `when`(rs.getTimestamp(1)).thenReturn(timestamp)
        `when`(rs.wasNull()).thenReturn(false)

        val result = SnowflakeOffsetDateTimeFieldType.jdbcGetter.get(rs, 1)

        assertEquals(ZoneOffset.UTC, result?.offset)
        assertEquals(500001000, result?.nano) // rounded up to microsecond precision
    }
}
