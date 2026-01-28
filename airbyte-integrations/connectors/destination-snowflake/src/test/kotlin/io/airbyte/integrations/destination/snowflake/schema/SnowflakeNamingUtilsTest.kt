/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeNamingUtilsTest {

    @Test
    fun `test empty string throws exception`() {
        assertThrows<ConfigErrorException> { "".toSnowflakeCompatibleName() }
    }

    @Test
    fun `test basic string is uppercased`() {
        assertEquals("HELLO", "hello".toSnowflakeCompatibleName())
        assertEquals("HELLO", "Hello".toSnowflakeCompatibleName())
        assertEquals("HELLO", "HELLO".toSnowflakeCompatibleName())
    }

    @Test
    fun `test dollar sign bigram replacement`() {
        // ${test} -> _test_ ($ replaced with _, { replaced with _, } replaced with _) -> __TEST_
        assertEquals("__TEST_", "\${test}".toSnowflakeCompatibleName())
    }

    @ParameterizedTest
    @CsvSource(
        "current_date, _CURRENT_DATE",
        "CURRENT_DATE, _CURRENT_DATE",
        "Current_Date, _CURRENT_DATE",
        "current_time, _CURRENT_TIME",
        "CURRENT_TIME, _CURRENT_TIME",
        "current_timestamp, _CURRENT_TIMESTAMP",
        "CURRENT_TIMESTAMP, _CURRENT_TIMESTAMP",
        "current_user, _CURRENT_USER",
        "CURRENT_USER, _CURRENT_USER",
    )
    fun `test reserved keywords are prefixed with underscore`(input: String, expected: String) {
        assertEquals(expected, input.toSnowflakeCompatibleName())
    }

    @Test
    fun `test non-reserved keywords are not prefixed`() {
        assertEquals("JOIN", "join".toSnowflakeCompatibleName())
        assertEquals("SELECT", "select".toSnowflakeCompatibleName())
        assertEquals("FROM", "from".toSnowflakeCompatibleName())
        assertEquals("DATE", "date".toSnowflakeCompatibleName())
        assertEquals("MY_CURRENT_DATE", "my_current_date".toSnowflakeCompatibleName())
        assertEquals("CURRENT_DATE_VALUE", "current_date_value".toSnowflakeCompatibleName())
    }

    @Test
    fun `test double quotes are escaped`() {
        assertEquals("TEST\"\"COLUMN", "test\"column".toSnowflakeCompatibleName())
    }
}
