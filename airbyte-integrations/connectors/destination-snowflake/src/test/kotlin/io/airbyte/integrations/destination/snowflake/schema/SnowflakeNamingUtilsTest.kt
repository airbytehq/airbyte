/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeNamingUtilsTest {
    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "localtime",
                "localtimestamp",
                "current_date",
                "current_time",
                "current_timestamp",
                "current_user",
            ]
    )
    fun `ansi reserved column names are prefixed with underscore`(name: String) {
        assertEquals("_${name.uppercase()}", name.toSnowflakeCompatibleName())
    }
}
