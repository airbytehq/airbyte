/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.integrations.source.mssql.MsSqlSourceOperations.MsSqlServerLocalDateTimeAccessor
import java.sql.ResultSet
import java.sql.Timestamp
import java.time.LocalDateTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class MsSqlServerLocalDateTimeAccessorTest {

    @Test
    fun `test truncates datetime with 7 decimal places to 6 decimal places`() {
        // Create a LocalDateTime with 7 decimal places (123456789 nanoseconds)
        val dateTimeWith7Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456789)
        val timestamp = Timestamp.valueOf(dateTimeWith7Decimals)

        val resultSet = mock(ResultSet::class.java)
        `when`(resultSet.getTimestamp(1)).thenReturn(timestamp)
        `when`(resultSet.wasNull()).thenReturn(false)

        val result = MsSqlServerLocalDateTimeAccessor.get(resultSet, 1)

        // Expected: truncated to microseconds (6 decimal places = 123456000 nanoseconds)
        val expected = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456000)

        assertEquals(expected, result)
        assertEquals(123456000, result?.nano)
    }

    @Test
    fun `test handles datetime with 6 decimal places correctly`() {
        // Create a LocalDateTime with exactly 6 decimal places (123456000 nanoseconds)
        val dateTimeWith6Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123456000)
        val timestamp = Timestamp.valueOf(dateTimeWith6Decimals)

        val resultSet = mock(ResultSet::class.java)
        `when`(resultSet.getTimestamp(1)).thenReturn(timestamp)
        `when`(resultSet.wasNull()).thenReturn(false)

        val result = MsSqlServerLocalDateTimeAccessor.get(resultSet, 1)

        // Should remain unchanged
        assertEquals(dateTimeWith6Decimals, result)
        assertEquals(123456000, result?.nano)
    }

    @Test
    fun `test handles datetime with less than 6 decimal places`() {
        // Create a LocalDateTime with 3 decimal places (123000000 nanoseconds)
        val dateTimeWith3Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 123000000)
        val timestamp = Timestamp.valueOf(dateTimeWith3Decimals)

        val resultSet = mock(ResultSet::class.java)
        `when`(resultSet.getTimestamp(1)).thenReturn(timestamp)
        `when`(resultSet.wasNull()).thenReturn(false)

        val result = MsSqlServerLocalDateTimeAccessor.get(resultSet, 1)

        // Should remain unchanged
        assertEquals(dateTimeWith3Decimals, result)
        assertEquals(123000000, result?.nano)
    }

    @Test
    fun `test handles null timestamp`() {
        val resultSet = mock(ResultSet::class.java)
        `when`(resultSet.getTimestamp(1)).thenReturn(null)
        `when`(resultSet.wasNull()).thenReturn(true)

        val result = MsSqlServerLocalDateTimeAccessor.get(resultSet, 1)

        assertEquals(null, result)
    }

    @Test
    fun `test datetime2 with maximum precision 7 digits`() {
        // SQL Server datetime2(7) can have up to 9999999 nanoseconds (7 decimal places)
        val dateTimeMaxPrecision = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 9999999)
        val timestamp = Timestamp.valueOf(dateTimeMaxPrecision)

        val resultSet = mock(ResultSet::class.java)
        `when`(resultSet.getTimestamp(1)).thenReturn(timestamp)
        `when`(resultSet.wasNull()).thenReturn(false)

        val result = MsSqlServerLocalDateTimeAccessor.get(resultSet, 1)

        // Expected: truncated to microseconds (999999 * 1000 = 999999000 nanoseconds)
        val expected = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 9999000)

        assertEquals(expected, result)
        assertEquals(9999000, result?.nano)
    }

    @Test
    fun `test formats truncated datetime correctly for BigQuery compatibility`() {
        // This is the actual failing case from the log:
        // "2025-11-06T22:30:46.0033333" (7 decimals) should become "2025-11-06T22:30:46.003333" (6
        // decimals)
        val dateTimeWith7Decimals = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 3333333)
        val timestamp = Timestamp.valueOf(dateTimeWith7Decimals)

        val resultSet = mock(ResultSet::class.java)
        `when`(resultSet.getTimestamp(1)).thenReturn(timestamp)
        `when`(resultSet.wasNull()).thenReturn(false)

        val result = MsSqlServerLocalDateTimeAccessor.get(resultSet, 1)

        // Expected: truncated to 3333000 nanoseconds (003333 microseconds)
        val expected = LocalDateTime.of(2025, 11, 6, 22, 30, 46, 3333000)

        assertEquals(expected, result)
        assertEquals(3333000, result?.nano)

        // Verify it formats correctly with the standard codec pattern
        val formatter = io.airbyte.cdk.data.LocalDateTimeCodec.formatter
        val formattedResult = result?.format(formatter)
        assertEquals("2025-11-06T22:30:46.003333", formattedResult)
    }
}
