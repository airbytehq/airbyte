/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import java.util.concurrent.CountDownLatch
import java.util.concurrent.CyclicBarrier
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
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

    /**
     * Stress test: multiple threads concurrently allocating and over-freeing memory. Verifies that
     * currentMemoryBytes never goes negative even under contention, and that backpressure
     * (requestMemory returning 0) still works correctly.
     */
    @Test
    internal fun concurrentAllocateAndOverFreeNeverGoesNegative() {
        val mgr = GlobalMemoryManager(20 * BYTES_MB)
        val threadCount = 8
        val iterationsPerThread = 1000
        val sawNegative = AtomicBoolean(false)
        val barrier = CyclicBarrier(threadCount)
        val executor = Executors.newFixedThreadPool(threadCount)
        val latch = CountDownLatch(threadCount)

        repeat(threadCount) { threadIndex ->
            executor.submit {
                try {
                    barrier.await() // start all threads simultaneously
                    for (i in 0 until iterationsPerThread) {
                        if (threadIndex % 2 == 0) {
                            // Allocator threads
                            mgr.requestMemory()
                        } else {
                            // Over-freeing threads — free more than what's likely allocated
                            mgr.free(3 * BYTES_MB)
                        }
                        // Check invariant: currentMemoryBytes must never be negative
                        if (mgr.getCurrentMemoryBytes() < 0) {
                            sawNegative.set(true)
                        }
                    }
                } catch (e: Exception) {
                    sawNegative.set(true)
                } finally {
                    latch.countDown()
                }
            }
        }

        latch.await(30, TimeUnit.SECONDS)
        executor.shutdownNow()

        Assertions.assertFalse(
            sawNegative.get(),
            "currentMemoryBytes went negative during concurrent access"
        )
        Assertions.assertTrue(
            mgr.getCurrentMemoryBytes() >= 0,
            "currentMemoryBytes is negative after concurrent test: ${mgr.getCurrentMemoryBytes()}"
        )

        // After the storm, the manager should still function correctly:
        // free everything and verify a fresh allocation works
        mgr.free(mgr.getCurrentMemoryBytes())
        Assertions.assertEquals(0, mgr.getCurrentMemoryBytes())
        Assertions.assertEquals(10 * BYTES_MB, mgr.requestMemory())
    }
}
