/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeSqlNameTransformerTest {

    private lateinit var transformer: SnowflakeSqlNameTransformer

    @BeforeEach
    fun setUp() {
        transformer = SnowflakeSqlNameTransformer()
    }

    @Test
    fun testToAlphanumericAndUnderscore() {
        assertEquals("users", transformer.transform("users"))
        assertEquals("users123", transformer.transform("users123"))
        assertEquals("UsErS", transformer.transform("UsErS"))
        assertEquals("users_USE_special_____", transformer.transform("users USE special !@#$"))
    }

    @Test
    fun testNameWithUnsupportedFirstCharacter() {
        val name = "-name-with-unsupported-first-character"
        assertEquals(
            "_${name.takeLast(name.length - 1).replace("-","_")}",
            transformer.transform(name)
        )
    }
}
