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
        val mgr = GlobalMemoryManager(20 * BYTES_MB)

        // Allocate 10 MB
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(10 * BYTES_MB, mgr.getCurrentMemoryBytes())

        // Free 15 MB (more than the 10 MB allocated) — should clamp to 0, not go to -5 MB
        mgr.free(15 * BYTES_MB)
        Assertions.assertEquals(0, mgr.getCurrentMemoryBytes())

        // Verify that requestMemory still works correctly after clamping
        // (previously, negative values would allow unbounded allocation)
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(10 * BYTES_MB, mgr.getCurrentMemoryBytes())
    }

    @Test
    internal fun repeatedOverFreeDoesNotAccumulateNegativeDebt() {
        val mgr = GlobalMemoryManager(20 * BYTES_MB)

        mgr.requestMemory() // 10 MB allocated

        // Simulate the bug: multiple over-frees that previously drove the counter deeply negative
        mgr.free(5 * BYTES_MB)
        mgr.free(5 * BYTES_MB)
        mgr.free(5 * BYTES_MB) // this one over-frees by 5 MB
        mgr.free(5 * BYTES_MB) // this one over-frees by 5 MB

        // Should be clamped at 0, not at -10 MB
        Assertions.assertEquals(0, mgr.getCurrentMemoryBytes())

        // Should be able to allocate exactly up to max
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
        Assertions.assertEquals(0, mgr.requestMemory()) // full
    }
}
