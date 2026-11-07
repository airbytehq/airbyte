/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.sql

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class FireboltSqlEscapeUtilsTest {

    @Test
    fun `quoteIdentifier wraps in double quotes`() {
        assertEquals("\"my_table\"", FireboltSqlEscapeUtils.quoteIdentifier("my_table"))
    }

    @Test
    fun `quoteIdentifier escapes embedded double quotes`() {
        assertEquals("\"my\"\"table\"", FireboltSqlEscapeUtils.quoteIdentifier("my\"table"))
    }

    @Test
    fun `escapeSqlString doubles single quotes`() {
        assertEquals("O''Brien", FireboltSqlEscapeUtils.escapeSqlString("O'Brien"))
    }
}
