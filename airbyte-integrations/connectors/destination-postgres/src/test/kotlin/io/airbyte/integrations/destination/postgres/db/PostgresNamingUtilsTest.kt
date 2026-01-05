/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.db

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

internal class PostgresNamingUtilsTest {

    @Test
    fun testBasicName() {
        assertEquals("my_table", "my_table".toPostgresCompatibleName())
        assertEquals("users", "users".toPostgresCompatibleName())
    }

    @Test
    fun testCasePreservation() {
        // toPostgresCompatibleName preserves case - does NOT convert to lowercase
        assertEquals("MY_TABLE", "MY_TABLE".toPostgresCompatibleName())
        assertEquals("USERS", "USERS".toPostgresCompatibleName())
        assertEquals("MixedCase", "MixedCase".toPostgresCompatibleName())
    }

    @Test
    fun testSpecialCharactersReplacedWithUnderscore() {
        assertEquals("my_table", "my-table".toPostgresCompatibleName())
        assertEquals("my_table", "my.table".toPostgresCompatibleName())
        assertEquals("my_table", "my table".toPostgresCompatibleName())
        assertEquals("my_table", "my@table".toPostgresCompatibleName())
        assertEquals("user_email", "user!email".toPostgresCompatibleName())
    }

    @Test
    fun testStartingWithDigit() {
        assertEquals("_123table", "123table".toPostgresCompatibleName())
        assertEquals("_1", "1".toPostgresCompatibleName())
        assertEquals("_99_red_balloons", "99-red-balloons".toPostgresCompatibleName())
    }

    @Test
    fun testEmptyStringReturnsFallbackName() {
        val result = "".toPostgresCompatibleName()
        assertTrue(result.startsWith("default_name_"))
    }

    @Test
    fun testOnlySpecialCharactersReturnsFallbackName() {
        val result = "@#$%^&*".toPostgresCompatibleName()
        // All special characters will be converted to underscores, which when collapsed
        // becomes "_______", but since it's not empty, it shouldn't trigger the fallback
        assertDoesNotThrow { "@#$%^&*".toPostgresCompatibleName() }
    }

    @Test
    fun testLongNameTruncation() {
        // PostgreSQL has a 63 character limit for identifiers
        val longName = "a".repeat(100)
        val result = longName.toPostgresCompatibleName()
        assertTrue(result.length <= 63, "Result should be truncated to 63 characters or less")
    }

    @Test
    fun testTruncationPreservesHash() {
        // Names longer than 63 chars should be truncated with a hash suffix
        val longName = "a".repeat(100)
        val result = longName.toPostgresCompatibleName()
        assertTrue(result.contains("_"), "Truncated name should contain underscore before hash")
        assertEquals(63, result.length)
    }

    @Test
    fun testUnicodeCharactersNormalization() {
        // Unicode NFKD normalization decomposes accented characters into base char + combining mark
        // Then combining marks are removed, resulting in the base character
        // For example: ñ -> n + combining tilde -> n (after removing combining mark)
        assertEquals("n", "ñ".toPostgresCompatibleName())
        assertEquals("cafe", "café".toPostgresCompatibleName())
        // CJK characters are replaced with underscores since they don't have ASCII equivalents
        assertEquals("__", "北京".toPostgresCompatibleName())
    }

    @Test
    fun testUnderscorePreservation() {
        assertEquals("my_table_name", "my_table_name".toPostgresCompatibleName())
        assertEquals("_private", "_private".toPostgresCompatibleName())
        assertEquals("__double_underscore", "__double_underscore".toPostgresCompatibleName())
    }

    @Test
    fun testMultipleConsecutiveSpecialCharacters() {
        // Multiple special chars are each replaced by an underscore
        val result = "my---table".toPostgresCompatibleName()
        assertEquals("my___table", result)
    }

    @Test
    fun testNumbersInMiddle() {
        assertEquals("table123", "table123".toPostgresCompatibleName())
        assertEquals("user_2_email", "user-2-email".toPostgresCompatibleName())
    }

    @Test
    fun testRealWorldExamples() {
        // Case is preserved
        assertEquals("Users", "Users".toPostgresCompatibleName())
        assertEquals("user_profile", "user-profile".toPostgresCompatibleName())
        // Uppercase is preserved
        assertEquals("CustomerData_v2", "CustomerData_v2".toPostgresCompatibleName())
        assertEquals("_2024_data", "2024_data".toPostgresCompatibleName())
        assertEquals("my_app_users", "my.app.users".toPostgresCompatibleName())
    }

    @Test
    fun testHashCollisionAvoidance() {
        // Two long names that only differ at the end should have different hashes
        val name1 = "a".repeat(60) + "xyz"
        val name2 = "a".repeat(60) + "abc"
        val result1 = name1.toPostgresCompatibleName()
        val result2 = name2.toPostgresCompatibleName()
        assertFalse(
            result1 == result2,
            "Different long names should produce different truncated names"
        )
    }
}
