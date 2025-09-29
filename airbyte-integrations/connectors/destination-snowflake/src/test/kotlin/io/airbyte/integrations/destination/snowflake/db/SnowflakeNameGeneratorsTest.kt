/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeNameGeneratorsTest {

    @ParameterizedTest
    @CsvSource(
        value =
            [
                "test-name,test_name",
                "1-test-name,_1_test_name",
                "test-name!!!,test_name___",
            ]
    )
    fun testToSnowflakeCompatibleName(name: String, expected: String) {
        assertEquals(expected, name.toSnowflakeCompatibleName())
    }

    @Test
    fun testEmptyNameToSnowflakeCompatibleName() {
        val name = "".toSnowflakeCompatibleName()
        assertTrue(name.startsWith("default_name_"))
    }
}
