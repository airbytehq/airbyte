/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class LimitsTest {

    private fun makeTimestampValue(ts: LocalDateTime): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = TimestampWithoutTimezoneValue(ts),
            type = TimestampTypeWithoutTimezone,
            name = "test_timestamp",
            airbyteMetaField = null,
        )

    private fun makeDateValue(date: LocalDate): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = DateValue(date),
            type = DateType,
            name = "test_date",
            airbyteMetaField = null,
        )

    private fun makeTimeWithTimezoneValue(time: OffsetTime): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = TimeWithTimezoneValue(time),
            type = TimeTypeWithTimezone,
            name = "test_time_tz",
            airbyteMetaField = null,
        )

    private fun makeTimeWithoutTimezoneValue(time: LocalTime): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = TimeWithoutTimezoneValue(time),
            type = TimeTypeWithoutTimezone,
            name = "test_time",
            airbyteMetaField = null,
        )

    private fun makeTimestampWithTimezoneValue(ts: OffsetDateTime): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = TimestampWithTimezoneValue(ts),
            type = TimestampTypeWithTimezone,
            name = "test_ts_tz",
            airbyteMetaField = null,
        )

    // --- validateTimestamp (existing tests) ---

    @Test
    fun `validateTimestamp passes through value within DATETIME range`() {
        val value = makeTimestampValue(LocalDateTime.of(2023, 6, 15, 12, 34, 56))
        val result = LIMITS.validateTimestamp(value)
        assertNotNull(result)
        assertEquals(LocalDateTime.of(2023, 6, 15, 12, 34, 56), result)
        assertTrue(value.abValue is TimestampWithoutTimezoneValue)
    }

    @Test
    fun `validateTimestamp passes through value at exact lower boundary`() {
        val value = makeTimestampValue(LocalDateTime.of(1753, 1, 1, 0, 0, 0))
        val result = LIMITS.validateTimestamp(value)
        assertNotNull(result)
        assertEquals(LocalDateTime.of(1753, 1, 1, 0, 0, 0), result)
        assertTrue(value.abValue is TimestampWithoutTimezoneValue)
    }

    @Test
    fun `validateTimestamp nullifies value below DATETIME lower boundary`() {
        val value = makeTimestampValue(LocalDateTime.of(1752, 12, 31, 23, 59, 59))
        val result = LIMITS.validateTimestamp(value)
        assertNull(result)
        assertTrue(value.abValue is NullValue)
        assertEquals(1, value.changes.size)
    }

    @Test
    fun `validateTimestamp nullifies pre-1753 date`() {
        val value = makeTimestampValue(LocalDateTime.of(1, 1, 1, 0, 0, 0))
        val result = LIMITS.validateTimestamp(value)
        assertNull(result)
        assertTrue(value.abValue is NullValue)
        assertEquals(1, value.changes.size)
    }

    // --- validateDate ---

    @Test
    fun `validateDate passes through valid date`() {
        val value = makeDateValue(LocalDate.of(2023, 6, 15))
        val result = LIMITS.validateDate(value)
        assertNotNull(result)
        assertEquals(LocalDate.of(2023, 6, 15), result)
        assertTrue(value.abValue is DateValue)
    }

    @Test
    fun `validateDate passes through MIN_DATE boundary`() {
        val value = makeDateValue(LocalDate.of(1, 1, 1))
        val result = LIMITS.validateDate(value)
        assertNotNull(result)
        assertEquals(LocalDate.of(1, 1, 1), result)
    }

    @Test
    fun `validateDate passes through MAX_DATE boundary`() {
        val value = makeDateValue(LocalDate.of(9999, 12, 31))
        val result = LIMITS.validateDate(value)
        assertNotNull(result)
        assertEquals(LocalDate.of(9999, 12, 31), result)
    }

    @Test
    fun `validateDate nullifies when abValue is not a DateValue`() {
        val value =
            EnrichedAirbyteValue(
                abValue = StringValue(""),
                type = DateType,
                name = "test_date",
                airbyteMetaField = null,
            )
        val result = LIMITS.validateDate(value)
        assertNull(result)
        assertTrue(value.abValue is NullValue)
        assertEquals(1, value.changes.size)
    }

    @Test
    fun `validateDate nullifies when abValue is a non-empty invalid string`() {
        val value =
            EnrichedAirbyteValue(
                abValue = StringValue("not-a-date"),
                type = DateType,
                name = "test_date",
                airbyteMetaField = null,
            )
        val result = LIMITS.validateDate(value)
        assertNull(result)
        assertTrue(value.abValue is NullValue)
        assertEquals(1, value.changes.size)
    }

    // --- validateTimeWithTimezone ---

    @Test
    fun `validateTimeWithTimezone passes through valid time`() {
        val time = OffsetTime.of(12, 30, 0, 0, ZoneOffset.UTC)
        val value = makeTimeWithTimezoneValue(time)
        val result = LIMITS.validateTimeWithTimezone(value)
        assertNotNull(result)
        assertEquals(time, result)
    }

    @Test
    fun `validateTimeWithTimezone nullifies when abValue is not TimeWithTimezoneValue`() {
        val value =
            EnrichedAirbyteValue(
                abValue = StringValue(""),
                type = TimeTypeWithTimezone,
                name = "test_time_tz",
                airbyteMetaField = null,
            )
        val result = LIMITS.validateTimeWithTimezone(value)
        assertNull(result)
        assertTrue(value.abValue is NullValue)
        assertEquals(1, value.changes.size)
    }

    // --- validateTimeWithoutTimezone ---

    @Test
    fun `validateTimeWithoutTimezone passes through valid time`() {
        val time = LocalTime.of(14, 30, 0)
        val value = makeTimeWithoutTimezoneValue(time)
        val result = LIMITS.validateTimeWithoutTimezone(value)
        assertNotNull(result)
        assertEquals(time, result)
    }

    @Test
    fun `validateTimeWithoutTimezone nullifies when abValue is not TimeWithoutTimezoneValue`() {
        val value =
            EnrichedAirbyteValue(
                abValue = StringValue(""),
                type = TimeTypeWithoutTimezone,
                name = "test_time",
                airbyteMetaField = null,
            )
        val result = LIMITS.validateTimeWithoutTimezone(value)
        assertNull(result)
        assertTrue(value.abValue is NullValue)
        assertEquals(1, value.changes.size)
    }

    // --- validateTimestampWithTimezone ---

    @Test
    fun `validateTimestampWithTimezone passes through valid timestamp`() {
        val ts = OffsetDateTime.of(2023, 6, 15, 12, 0, 0, 0, ZoneOffset.UTC)
        val value = makeTimestampWithTimezoneValue(ts)
        val result = LIMITS.validateTimestampWithTimezone(value)
        assertNotNull(result)
        assertEquals(ts, result)
    }

    @Test
    fun `validateTimestampWithTimezone nullifies when abValue is not TimestampWithTimezoneValue`() {
        val value =
            EnrichedAirbyteValue(
                abValue = StringValue(""),
                type = TimestampTypeWithTimezone,
                name = "test_ts_tz",
                airbyteMetaField = null,
            )
        val result = LIMITS.validateTimestampWithTimezone(value)
        assertNull(result)
        assertTrue(value.abValue is NullValue)
        assertEquals(1, value.changes.size)
    }
}
