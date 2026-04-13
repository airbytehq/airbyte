/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class RedshiftSqlEscapeUtilsTest {

    @Test
    fun `quoteIdentifier wraps in double quotes`() {
        assertEquals("\"my_table\"", RedshiftSqlEscapeUtils.quoteIdentifier("my_table"))
    }

    @Test
    fun `quoteIdentifier escapes embedded double quotes`() {
        assertEquals("\"my\"\"col\"", RedshiftSqlEscapeUtils.quoteIdentifier("my\"col"))
    }

    @Test
    fun `quoteIdentifier handles empty string`() {
        assertEquals("\"\"", RedshiftSqlEscapeUtils.quoteIdentifier(""))
    }

    @Test
    fun `escapeSqlString doubles single quotes`() {
        assertEquals("O''Brien", RedshiftSqlEscapeUtils.escapeSqlString("O'Brien"))
    }

    @Test
    fun `escapeSqlString handles no quotes`() {
        assertEquals("hello", RedshiftSqlEscapeUtils.escapeSqlString("hello"))
    }

    @Test
    fun `escapeSqlString handles multiple quotes`() {
        assertEquals("it''s a ''test''", RedshiftSqlEscapeUtils.escapeSqlString("it's a 'test'"))
    }
}
