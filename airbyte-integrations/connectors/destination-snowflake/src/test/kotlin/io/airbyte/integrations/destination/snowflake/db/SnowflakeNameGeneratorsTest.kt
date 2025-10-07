/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeNameGeneratorsTest {

    @ParameterizedTest
    @CsvSource(
        value =
            [
                "test-name,TEST-NAME",
                "1-test-name,1-TEST-NAME",
                "test-name!!!,TEST-NAME!!!",
                "test\${name,TEST__NAME",
                "test\"name,TEST\"\"NAME",
            ]
    )
    fun testToSnowflakeCompatibleName(name: String, expected: String) {
        assertEquals(expected, name.toSnowflakeCompatibleName())
    }
}
