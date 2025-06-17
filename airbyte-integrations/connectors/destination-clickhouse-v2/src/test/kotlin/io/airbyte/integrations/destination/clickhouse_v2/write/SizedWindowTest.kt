/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write

import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

class SizedWindowTest {
    @Test
    fun `is complete once incremented to the specified size`() {
        val window = SizedWindow(100)
        window.increment(1)
        assertFalse(window.isComplete())
        window.increment(20)
        window.increment(30)
        assertFalse(window.isComplete())
        window.increment(29)
        assertFalse(window.isComplete())
        window.increment(20)
        assertTrue(window.isComplete())
        window.increment(10)
        assertTrue(window.isComplete())
    }
}
