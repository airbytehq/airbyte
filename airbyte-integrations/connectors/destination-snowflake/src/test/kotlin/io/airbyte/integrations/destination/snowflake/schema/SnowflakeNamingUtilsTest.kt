/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeNamingUtilsTest {

    @ParameterizedTest
    @CsvSource(
        "current_date, _CURRENT_DATE",
        "current_time, _CURRENT_TIME",
        "current_timestamp, _CURRENT_TIMESTAMP",
        "current_user, _CURRENT_USER",
        "localtime, _LOCALTIME",
        "localtimestamp, _LOCALTIMESTAMP",
        "constraint, _CONSTRAINT",
    )
    fun `reserved keywords are prefixed with underscore`(input: String, expected: String) {
        assertEquals(expected, input.toSnowflakeCompatibleName())
    }

    @ParameterizedTest
    @CsvSource(
        "CURRENT_DATE, _CURRENT_DATE",
        "CURRENT_TIME, _CURRENT_TIME",
        "CURRENT_TIMESTAMP, _CURRENT_TIMESTAMP",
        "CURRENT_USER, _CURRENT_USER",
        "LOCALTIME, _LOCALTIME",
        "LOCALTIMESTAMP, _LOCALTIMESTAMP",
        "CONSTRAINT, _CONSTRAINT",
    )
    fun `uppercase reserved keywords are prefixed with underscore`(
        input: String,
        expected: String
    ) {
        assertEquals(expected, input.toSnowflakeCompatibleName())
    }

    @Test
    fun `non-reserved keywords are not prefixed`() {
        assertEquals("MY_COLUMN", "my_column".toSnowflakeCompatibleName())
        assertEquals("JOIN", "join".toSnowflakeCompatibleName())
        assertEquals("SELECT", "select".toSnowflakeCompatibleName())
        assertEquals("TABLE", "table".toSnowflakeCompatibleName())
    }

    @Test
    fun `partial matches of reserved keywords are not prefixed`() {
        assertEquals("MY_CURRENT_DATE", "my_current_date".toSnowflakeCompatibleName())
        assertEquals("CURRENT_DATE_FIELD", "current_date_field".toSnowflakeCompatibleName())
        assertEquals("XCURRENT_USER", "xcurrent_user".toSnowflakeCompatibleName())
        assertEquals("LOCALTIMESTAMPX", "localtimestampx".toSnowflakeCompatibleName())
    }

    @Test
    fun `regular identifiers are uppercased`() {
        assertEquals("FOO", "foo".toSnowflakeCompatibleName())
        assertEquals("BAR_BAZ", "bar_baz".toSnowflakeCompatibleName())
    }

    @Test
    fun `empty string throws exception`() {
        assertThrows(ConfigErrorException::class.java) { "".toSnowflakeCompatibleName() }
    }

    @Test
    fun `dollar sign bigram is handled`() {
        val result = "\${foo}".toSnowflakeCompatibleName()
        assertEquals("__FOO_", result)
    }

    @Test
    fun `double quotes are escaped`() {
        val result = "col\"name".toSnowflakeCompatibleName()
        assertEquals("COL\"\"NAME", result)
    }
}
