/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.schema

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DorisNamingUtilsTest {

    @Test
    fun `simple name is unchanged`() {
        assertEquals("my_table", "my_table".toDorisCompatibleName())
    }

    @Test
    fun `special characters are replaced`() {
        val result = "my-table.name!".toDorisCompatibleName()
        assertFalse(result.contains("-"))
        assertFalse(result.contains("."))
        assertFalse(result.contains("!"))
    }

    @Test
    fun `leading digit gets underscore prefix`() {
        val result = "123table".toDorisCompatibleName()
        assertTrue(result.startsWith("_"))
    }

    @Test
    fun `empty string gets default name`() {
        val result = "".toDorisCompatibleName()
        assertTrue(result.startsWith("default_name_"))
    }

    @Test
    fun `alphanumeric and underscores are preserved`() {
        assertEquals("abc_123_XYZ", "abc_123_XYZ".toDorisCompatibleName())
    }
}
