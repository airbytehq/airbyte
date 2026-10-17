/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import io.airbyte.integrations.source.postgres.operations.types.PgTimestampCodec
import io.airbyte.integrations.source.postgres.operations.types.parseTimestampWithDateFallback
import java.time.LocalDateTime
import java.time.format.DateTimeParseException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class PostgresTimestampFieldTypeTest {

    @Test
    fun `parseTimestampWithDateFallback parses full datetime string`() {
        val result = parseTimestampWithDateFallback("2026-08-12T10:30:45")
        assertEquals(LocalDateTime.of(2026, 8, 12, 10, 30, 45), result)
    }

    @Test
    fun `parseTimestampWithDateFallback parses datetime with fractional seconds`() {
        val result = parseTimestampWithDateFallback("2026-08-12T10:30:45.123456")
        assertEquals(LocalDateTime.of(2026, 8, 12, 10, 30, 45, 123456000), result)
    }

    @Test
    fun `parseTimestampWithDateFallback parses date-only string with fallback`() {
        val result = parseTimestampWithDateFallback("2026-08-12")
        assertEquals(LocalDateTime.of(2026, 8, 12, 0, 0, 0), result)
    }

    @Test
    fun `parseTimestampWithDateFallback throws on unparseable input`() {
        val exception =
            assertThrows(DateTimeParseException::class.java) {
                parseTimestampWithDateFallback("not-a-date")
            }
        assert(exception.message!!.contains("Cannot parse timestamp value"))
    }

    @Test
    fun `PgTimestampCodec valueForProtobufEncoding handles date-only string`() {
        val result = PgTimestampCodec.valueForProtobufEncoding("2026-08-12")
        assertEquals(LocalDateTime.of(2026, 8, 12, 0, 0, 0), result)
    }

    @Test
    fun `PgTimestampCodec valueForProtobufEncoding handles full timestamp`() {
        val result = PgTimestampCodec.valueForProtobufEncoding("2026-08-12T10:30:45")
        assertEquals(LocalDateTime.of(2026, 8, 12, 10, 30, 45), result)
    }

    @Test
    fun `PgTimestampCodec valueForProtobufEncoding handles BCE date-only`() {
        val result = PgTimestampCodec.valueForProtobufEncoding("0044-03-15 BC")
        val expected = LocalDateTime.of(44, 3, 15, 0, 0, 0).withYear(1 - 44)
        assertEquals(expected, result)
    }

    @Test
    fun `PgTimestampCodec valueForProtobufEncoding handles BCE full timestamp`() {
        val result = PgTimestampCodec.valueForProtobufEncoding("0044-03-15T12:00:00 BC")
        val expected = LocalDateTime.of(44, 3, 15, 12, 0, 0).withYear(1 - 44)
        assertEquals(expected, result)
    }
}
