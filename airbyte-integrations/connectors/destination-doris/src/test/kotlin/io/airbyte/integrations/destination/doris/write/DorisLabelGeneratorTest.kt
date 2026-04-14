/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.write

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DorisLabelGeneratorTest {

    @Test
    fun `generateLabel creates valid label`() {
        val label = DorisLabelGenerator.generateLabel("my_table")
        assertTrue(label.startsWith("airbyte_my_table_"))
        assertTrue(label.length <= 128)
        assertTrue(label.matches(Regex("^[-_A-Za-z0-9]+$")))
    }

    @Test
    fun `generateLabel sanitizes special characters`() {
        val label = DorisLabelGenerator.generateLabel("my-table.name")
        assertTrue(label.startsWith("airbyte_my_table_name_"))
        assertFalse(label.contains("-") && label.contains("."))
    }

    @Test
    fun `generateLabel creates unique labels`() {
        val label1 = DorisLabelGenerator.generateLabel("test")
        val label2 = DorisLabelGenerator.generateLabel("test")
        assertFalse(label1 == label2)
    }

    @Test
    fun `retryLabel appends retry suffix`() {
        val original = "airbyte_test_abc123"
        val retry1 = DorisLabelGenerator.retryLabel(original, 1)
        val retry2 = DorisLabelGenerator.retryLabel(original, 2)
        assertEquals("${original}_r1", retry1)
        assertEquals("${original}_r2", retry2)
    }
}
