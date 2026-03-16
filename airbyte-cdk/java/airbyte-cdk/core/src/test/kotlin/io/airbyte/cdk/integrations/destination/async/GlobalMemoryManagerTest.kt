/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class GlobalMemoryManagerTest {
    private val BYTES_MB = (1024 * 1024).toLong()

    @Test
    internal fun test() {
        val mgr = GlobalMemoryManager(15 * BYTES_MB)

        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(5 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(0, mgr.requestMemory())

        mgr.free(10 * BYTES_MB)
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        mgr.free(16 * BYTES_MB)
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
    }

    @Test
    internal fun freeMoreThanAllocatedClampsToZero() {
        val mgr = GlobalMemoryManager(15 * BYTES_MB)

        // Allocate 10 MB, then free 20 MB — should clamp to 0, not go to -10 MB.
        mgr.requestMemory() // 10 MB allocated
        mgr.free(20 * BYTES_MB)
        Assertions.assertEquals(0, mgr.getCurrentMemoryBytes(), "currentMemoryBytes must not go negative")

        // Verify that subsequent allocations still work correctly after clamping.
        val allocated = mgr.requestMemory()
        Assertions.assertEquals(10 * BYTES_MB, allocated, "Should allocate a full block after clamping to zero")
    }

    @Test
    internal fun repeatedOverFreeDoesNotAccumulateNegativeDebt() {
        val mgr = GlobalMemoryManager(15 * BYTES_MB)

        // Simulate the production scenario: multiple rounds of over-freeing
        // that would previously accumulate negative debt.
        for (i in 1..5) {
            mgr.requestMemory() // 10 MB
            mgr.free(15 * BYTES_MB) // Over-free by 5 MB each time
            Assertions.assertTrue(
                mgr.getCurrentMemoryBytes() >= 0,
                "Iteration $i: currentMemoryBytes must not go negative",
            )
        }

        // After repeated over-frees, memory accounting should still be functional.
        val allocated = mgr.requestMemory()
        Assertions.assertTrue(allocated > 0, "Should still be able to allocate memory after repeated over-frees")
    }
}
