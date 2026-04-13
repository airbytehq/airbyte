/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class AirbyteValueCoercerTest {

    @Test
    fun `coerceTimestampTz rejects 5-digit year without plus prefix`() {
        // Year 22026 without + prefix - the DATE_TIME_FORMATTER pattern [yyyy] in SMART mode
        // could parse this as a valid 5-digit year. The coercer should reject it.
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("22026-12-06T00:00:00.000000Z"),
                TimestampTypeWithTimezone,
            )
        assertNull(result, "Timestamp with year 22026 (no + prefix) should be rejected")
    }

    @Test
    fun `coerceTimestampTz rejects 5-digit year with plus prefix`() {
        // Year 22026 with + prefix (ISO 8601 extended year format)
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("+22026-12-06T00:00:00.000000Z"),
                TimestampTypeWithTimezone,
            )
        assertNull(result, "Timestamp with year +22026 should be rejected")
    }

    @Test
    fun `coerceTimestampNtz rejects 5-digit year without plus prefix`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("22026-12-06T00:00:00.000000"),
                TimestampTypeWithoutTimezone,
            )
        assertNull(result, "Timestamp without timezone with year 22026 should be rejected")
    }

    @Test
    fun `coerceTimestampNtz rejects 5-digit year with plus prefix`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("+22026-12-06T00:00:00.000000"),
                TimestampTypeWithoutTimezone,
            )
        assertNull(result, "Timestamp without timezone with year +22026 should be rejected")
    }

    @Test
    fun `coerceDate rejects 5-digit year`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("22026-12-06"),
                DateType,
            )
        assertNull(result, "Date with year 22026 should be rejected")
    }

    @Test
    fun `coerceTimestampTz accepts valid 4-digit year timestamps`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("2024-06-15T12:30:00Z"),
                TimestampTypeWithTimezone,
            )
        assert(result is TimestampWithTimezoneValue) {
            "Valid timestamp should be accepted, got: $result"
        }
    }

    @Test
    fun `coerceTimestampTz accepts boundary year 9999`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("9999-12-31T23:59:59Z"),
                TimestampTypeWithTimezone,
            )
        assert(result is TimestampWithTimezoneValue) {
            "Year 9999 should be accepted, got: $result"
        }
    }

    @Test
    fun `coerceTimestampTz accepts boundary year 0001`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("0001-01-01T00:00:00Z"),
                TimestampTypeWithTimezone,
            )
        assert(result is TimestampWithTimezoneValue) {
            "Year 0001 should be accepted, got: $result"
        }
    }

    @Test
    fun `coerceTimestampTz rejects year 0000`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("0000-01-01T00:00:00Z"),
                TimestampTypeWithTimezone,
            )
        assertNull(result, "Year 0000 should be rejected")
    }

    @Test
    fun `coerceTimestampTz rejects year 10000`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("10000-01-01T00:00:00Z"),
                TimestampTypeWithTimezone,
            )
        assertNull(result, "Year 10000 should be rejected")
    }

    @Test
    fun `coerceDate accepts valid 4-digit year dates`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("2024-06-15"),
                DateType,
            )
        assert(result is DateValue) { "Valid date should be accepted, got: $result" }
    }

    @Test
    fun `coerceDate accepts boundary year 9999`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("9999-12-31"),
                DateType,
            )
        assert(result is DateValue) { "Year 9999 date should be accepted, got: $result" }
    }

    @Test
    fun `coerceDate rejects year 10000`() {
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("10000-01-01"),
                DateType,
            )
        assertNull(result, "Year 10000 date should be rejected")
    }

    @Test
    fun `coerce returns null for null coercion result`() {
        // null from coerce means the value couldn't be coerced
        val result =
            AirbyteValueCoercer.coerce(
                StringValue("not-a-timestamp"),
                TimestampTypeWithTimezone,
            )
        assertNull(result, "Invalid timestamp string should return null")
    }

    @Test
    fun `coerce passes through NullValue unchanged`() {
        val result = AirbyteValueCoercer.coerce(NullValue, TimestampTypeWithTimezone)
        assertEquals(NullValue, result, "NullValue should pass through unchanged")
    }
}
