/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import java.time.LocalDateTime
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
}
