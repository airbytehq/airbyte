/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.check

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class CheckOperationMessageTest {
    @Test
    fun testZeroTablesMessageWithOneNamespace() {
        assertEquals(
            "Discovered zero tables in 'appdbx'. Check that the database or schema name is correct " +
                "and contains tables, that the configured user has permission to list and select " +
                "them, and that table filters, if any, don't exclude all of them.",
            CheckOperation.zeroTablesMessage(listOf("appdbx")),
        )
    }

    @Test
    fun testZeroTablesMessageTruncatesNamespaces() {
        assertEquals(
            "Discovered zero tables in 'a', 'b', 'c', 'd', 'e' and 2 more. Check that the database " +
                "or schema name is correct and contains tables, that the configured user has " +
                "permission to list and select them, and that table filters, if any, don't exclude " +
                "all of them.",
            CheckOperation.zeroTablesMessage(listOf("a", "b", "c", "d", "e", "f", "g")),
        )
    }

    @Test
    fun testZeroTablesMessageWithoutNamespaces() {
        assertEquals(
            "Discovered zero tables. Check that the configured user has permission to list and " +
                "select tables, and that the database or schema selection and table filters, if " +
                "any, don't exclude all of them.",
            CheckOperation.zeroTablesMessage(emptyList()),
        )
    }
}
