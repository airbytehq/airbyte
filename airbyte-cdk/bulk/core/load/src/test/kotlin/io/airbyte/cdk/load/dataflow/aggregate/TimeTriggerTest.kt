/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class TimeTriggerTest {

    @Test
    fun `time trigger logic`() {
        val triggerSize = 1000L // 1 second
        val trigger = TimeTrigger(triggerSize)

        val startTime = System.currentTimeMillis()

        // Update the trigger with the start time
        trigger.update(startTime)

        // Immediately after update, it should not be complete
        assertFalse(trigger.isComplete(startTime))

        // Just before the trigger time, it should not be complete
        assertFalse(trigger.isComplete(startTime + triggerSize - 1))

        // Exactly at the trigger time, it should be complete
        assertTrue(trigger.isComplete(startTime + triggerSize))

        // After the trigger time, it should be complete
        assertTrue(trigger.isComplete(startTime + triggerSize + 1))
    }

    @Test
    fun `updating timestamp resets the trigger`() {
        val triggerSize = 1000L
        val trigger = TimeTrigger(triggerSize)

        val startTime = System.currentTimeMillis()
        trigger.update(startTime)

        // It should be complete after triggerSize
        assertTrue(trigger.isComplete(startTime + triggerSize))

        // Update the timestamp to a later time
        val newStartTime = startTime + 500L
        trigger.update(newStartTime)

        // Now it should not be complete relative to the new start time
        assertFalse(trigger.isComplete(newStartTime + triggerSize - 1))
        assertTrue(trigger.isComplete(newStartTime + triggerSize))
    }
}
