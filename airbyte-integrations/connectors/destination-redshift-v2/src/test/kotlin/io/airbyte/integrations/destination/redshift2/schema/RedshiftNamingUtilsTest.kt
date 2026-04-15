/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.schema

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class RedshiftNamingUtilsTest {

    @Test
    fun `basic alphanumeric name is lowercased`() {
        assertEquals("my_table", "my_table".toRedshiftCompatibleName())
    }

    @Test
    fun `mixed case name is lowercased`() {
        assertEquals("mytable", "MyTable".toRedshiftCompatibleName())
    }

    @Test
    fun `special characters replaced with underscores`() {
        assertEquals("my_table_name", "my-table.name".toRedshiftCompatibleName())
    }

    @Test
    fun `spaces replaced with underscores`() {
        assertEquals("my_table_name", "my table name".toRedshiftCompatibleName())
    }

    @Test
    fun `at sign and other symbols replaced`() {
        assertEquals("user_email_address", "user@email+address".toRedshiftCompatibleName())
    }

    @Test
    fun `digit prefixed name gets underscore prepended`() {
        assertEquals("_1foo", "1foo".toRedshiftCompatibleName())
    }

    @Test
    fun `already lowercase name unchanged`() {
        assertEquals("public", "public".toRedshiftCompatibleName())
    }

    @Test
    fun `unicode characters replaced with underscores`() {
        // Unicode characters that aren't simple alphanumeric are replaced
        val result = "table_\u00e9\u00e8".toRedshiftCompatibleName()
        // After NFKD normalization, accented chars decompose and combining marks are stripped
        assertEquals("table_ee", result)
    }

    @Test
    fun `underscores preserved`() {
        assertEquals("my_table_name", "my_table_name".toRedshiftCompatibleName())
    }

    @Test
    fun `consecutive special characters collapsed to underscores`() {
        assertEquals("a___b", "a---b".toRedshiftCompatibleName())
    }
}
