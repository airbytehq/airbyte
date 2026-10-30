/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.schema

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
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

    // ================================================================
    // Truncation (127-byte Redshift identifier limit)
    // ================================================================

    @Test
    fun `name exactly 127 chars is not truncated`() {
        val input = "a".repeat(127)
        val result = input.toRedshiftCompatibleName()
        assertEquals(127, result.length)
        assertEquals(input, result)
    }

    @Test
    fun `name exceeding 127 chars is truncated`() {
        val input = "a".repeat(200)
        val result = input.toRedshiftCompatibleName()
        assertTrue(result.length <= 127, "Expected <= 127 chars but got ${result.length}")
    }

    @Test
    fun `truncation is deterministic`() {
        val input = "x".repeat(200)
        val first = input.toRedshiftCompatibleName()
        val second = input.toRedshiftCompatibleName()
        assertEquals(first, second)
    }

    @Test
    fun `two long names sharing a prefix produce different truncated results`() {
        val base = "a".repeat(130)
        val input1 = base + "_suffix_one"
        val input2 = base + "_suffix_two"
        val result1 = input1.toRedshiftCompatibleName()
        val result2 = input2.toRedshiftCompatibleName()
        assertTrue(result1 != result2, "Expected different results for different inputs")
        assertTrue(result1.length <= 127)
        assertTrue(result2.length <= 127)
    }

    @Test
    fun `truncated name with digit prefix still prepends underscore and stays within limit`() {
        // Input starts with a digit and exceeds 127 chars after underscore prepend
        val input = "1" + "a".repeat(200)
        val result = input.toRedshiftCompatibleName()
        assertTrue(result.startsWith("_"), "Expected leading underscore for digit-prefixed name")
        assertTrue(result.length <= 127, "Expected <= 127 chars but got ${result.length}")
    }
}
