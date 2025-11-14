/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class SizeTriggerTest {
    @Test
    fun `trigger not fired when under threshold`() {
        val trigger = SizeTrigger(100)
        trigger.increment(50)
        assertFalse(trigger.isComplete())
        assertEquals(50L, trigger.watermark())
    }

    @Test
    fun `trigger fired when at threshold`() {
        val trigger = SizeTrigger(100)
        trigger.increment(100)
        assertTrue(trigger.isComplete())
        assertEquals(100L, trigger.watermark())
    }

    @Test
    fun `trigger fired when over threshold`() {
        val trigger = SizeTrigger(100)
        trigger.increment(150)
        assertTrue(trigger.isComplete())
        assertEquals(150L, trigger.watermark())
    }

    @Test
    fun `multiple increments`() {
        val trigger = SizeTrigger(100)
        trigger.increment(50)
        assertFalse(trigger.isComplete())
        assertEquals(50L, trigger.watermark())
        trigger.increment(49)
        assertFalse(trigger.isComplete())
        assertEquals(99L, trigger.watermark())
        trigger.increment(1)
        assertTrue(trigger.isComplete())
        assertEquals(100L, trigger.watermark())
    }
}
