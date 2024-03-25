/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.concurrency

import java.time.Duration
import java.util.function.Supplier
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.mock

internal class WaitingUtilsTest {
    @Test
    fun testWaitForConditionConditionMet() {
        val condition: Supplier<Boolean> = mock()
        Mockito.`when`(condition.get()).thenReturn(false).thenReturn(false).thenReturn(true)
        Assertions.assertTrue(
            WaitingUtils.waitForCondition(Duration.ofMillis(1), Duration.ofMillis(5), condition)
        )
    }

    @Test
    fun testWaitForConditionTimeout() {
        val condition: Supplier<Boolean> = mock()
        Mockito.`when`(condition.get()).thenReturn(false)
        Assertions.assertFalse(
            WaitingUtils.waitForCondition(Duration.ofMillis(1), Duration.ofMillis(5), condition)
        )
    }
}
