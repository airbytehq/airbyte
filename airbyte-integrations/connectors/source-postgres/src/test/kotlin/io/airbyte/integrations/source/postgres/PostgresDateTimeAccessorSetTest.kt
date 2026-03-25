/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.integrations.source.postgres.operations.types.PostgresDateFieldType
import io.airbyte.integrations.source.postgres.operations.types.PostgresTimestampFieldType
import io.airbyte.integrations.source.postgres.operations.types.PostgresTimestampTzFieldType
import io.mockk.confirmVerified
import io.mockk.mockk
import io.mockk.verify
import java.sql.PreparedStatement
import java.sql.Timestamp
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import org.junit.jupiter.api.Test

/**
 * Verifies that the Postgres-specific field type set() methods use typed JDBC setters
 * (setTimestamp, setDate) instead of setString. Using setString causes PostgreSQL to
 * reject cursor comparisons with:
 *   "operator does not exist: timestamp without time zone >= character varying"
 */
class PostgresDateTimeAccessorSetTest {

    @Test
    fun `PgTimestampFieldType set uses setTimestamp not setString`() {
        val stmt = mockk<PreparedStatement>(relaxed = true)
        val value = "2024-06-15T10:30:45.123456"
        PostgresTimestampFieldType.set(stmt, 1, TextNode(value))
        val expected = Timestamp.valueOf(LocalDateTime.parse(value))
        verify(exactly = 1) { stmt.setTimestamp(1, expected) }
        verify(exactly = 0) { stmt.setString(any(), any()) }
        confirmVerified(stmt)
    }

    @Test
    fun `PgTimestampFieldType set handles BCE timestamps`() {
        val stmt = mockk<PreparedStatement>(relaxed = true)
        val value = "0044-03-15T12:00:00 BC"
        PostgresTimestampFieldType.set(stmt, 1, TextNode(value))
        val parsed = LocalDateTime.parse("0044-03-15T12:00:00")
        val adjusted = parsed.withYear(1 - parsed.year)
        val expected = Timestamp.valueOf(adjusted)
        verify(exactly = 1) { stmt.setTimestamp(1, expected) }
        verify(exactly = 0) { stmt.setString(any(), any()) }
        confirmVerified(stmt)
    }

    @Test
    fun `PgDateFieldType set uses setDate not setString`() {
        val stmt = mockk<PreparedStatement>(relaxed = true)
        val value = "2024-06-15"
        PostgresDateFieldType.set(stmt, 1, TextNode(value))
        val expected = java.sql.Date.valueOf(LocalDate.parse(value))
        verify(exactly = 1) { stmt.setDate(1, expected) }
        verify(exactly = 0) { stmt.setString(any(), any()) }
        confirmVerified(stmt)
    }

    @Test
    fun `PgDateFieldType set handles BCE dates`() {
        val stmt = mockk<PreparedStatement>(relaxed = true)
        val value = "0044-03-15 BC"
        PostgresDateFieldType.set(stmt, 1, TextNode(value))
        val parsed = LocalDate.parse("0044-03-15")
        val adjusted = parsed.withYear(1 - parsed.year)
        val expected = java.sql.Date.valueOf(adjusted)
        verify(exactly = 1) { stmt.setDate(1, expected) }
        verify(exactly = 0) { stmt.setString(any(), any()) }
        confirmVerified(stmt)
    }

    @Test
    fun `PgTimestampTzFieldType set uses setTimestamp not setString`() {
        val stmt = mockk<PreparedStatement>(relaxed = true)
        val value = "2024-06-15T10:30:45.123456+00:00"
        PostgresTimestampTzFieldType.set(stmt, 1, TextNode(value))
        val odt = OffsetDateTime.parse(value)
        val expected = Timestamp.from(odt.toInstant())
        verify(exactly = 1) { stmt.setTimestamp(1, expected) }
        verify(exactly = 0) { stmt.setString(any(), any()) }
        confirmVerified(stmt)
    }

    @Test
    fun `PgTimestampTzFieldType set handles non-UTC offsets`() {
        val stmt = mockk<PreparedStatement>(relaxed = true)
        val value = "2024-06-15T10:30:45.000000+05:30"
        PostgresTimestampTzFieldType.set(stmt, 1, TextNode(value))
        val odt = OffsetDateTime.parse(value)
        val expected = Timestamp.from(odt.toInstant())
        verify(exactly = 1) { stmt.setTimestamp(1, expected) }
        verify(exactly = 0) { stmt.setString(any(), any()) }
        confirmVerified(stmt)
    }
}
