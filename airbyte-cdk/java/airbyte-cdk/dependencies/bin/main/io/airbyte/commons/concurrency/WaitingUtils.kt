/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.concurrency

import java.time.Duration
import java.util.function.Supplier

object WaitingUtils {
    /**
     * Wait for a condition or timeout.
     *
     * @param interval
     * - frequency with which condition and timeout should be checked.
     * @param timeout
     * - how long to wait in total
     * @param condition
     * - supplier that returns whether the condition has been met.
     * @return true if condition was met before the timeout was reached, otherwise false.
     */
    fun waitForCondition(
        interval: Duration,
        timeout: Duration,
        condition: Supplier<Boolean>
    ): Boolean {
        var timeWaited = Duration.ZERO
        while (true) {
            if (condition.get()) {
                return true
            }

            if (timeout.minus(timeWaited).isNegative) {
                return false
            }

            try {
                Thread.sleep(interval.toMillis())
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }

            timeWaited = timeWaited.plus(interval)
        }
    }
}
