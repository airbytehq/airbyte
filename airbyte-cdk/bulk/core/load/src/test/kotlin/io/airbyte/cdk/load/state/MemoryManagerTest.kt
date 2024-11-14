/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MemoryManagerTest {
    @Test
    fun testReserve() = runTest {
        val memoryManager = MemoryManager(1000)
        val reserved = AtomicBoolean(false)

        try {
            withTimeout(5000) { memoryManager.reserve(900, this) }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Failed to reserve memory")
        }

        Assertions.assertEquals(100, memoryManager.remainingMemoryBytes)

        val job = launch {
            memoryManager.reserve(200, this)
            reserved.set(true)
        }

        memoryManager.reserve(0, this)
        Assertions.assertFalse(reserved.get())

        memoryManager.release(50)
        memoryManager.reserve(0, this)
        Assertions.assertEquals(150, memoryManager.remainingMemoryBytes)
        Assertions.assertFalse(reserved.get())

        memoryManager.release(25)
        memoryManager.reserve(0, this)
        Assertions.assertEquals(175, memoryManager.remainingMemoryBytes)
        Assertions.assertFalse(reserved.get())

        memoryManager.release(25)
        try {
            withTimeout(5000) { job.join() }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Failed to unblock reserving memory")
        }
        Assertions.assertEquals(0, memoryManager.remainingMemoryBytes)
        Assertions.assertTrue(reserved.get())
    }

    @Test
    fun testReserveMultithreaded() = runTest {
        val memoryManager = MemoryManager(1000)
        withContext(Dispatchers.IO) {
            memoryManager.reserve(1000, this)
            Assertions.assertEquals(0, memoryManager.remainingMemoryBytes)
            val nIterations = 100000

            val jobs = (0 until nIterations).map { launch { memoryManager.reserve(10, this) } }

            repeat(nIterations) {
                memoryManager.release(10)
                Assertions.assertTrue(
                    memoryManager.remainingMemoryBytes >= 0,
                    "Remaining memory is negative: ${memoryManager.remainingMemoryBytes}"
                )
            }
            jobs.forEach { it.join() }
            Assertions.assertEquals(0, memoryManager.remainingMemoryBytes)
        }
    }

    @Test
    fun testRequestingMoreThanAvailableThrows() = runTest {
        val memoryManager = MemoryManager(1000)
        try {
            memoryManager.reserve(1001, this)
        } catch (e: IllegalArgumentException) {
            return@runTest
        }
        Assertions.fail<Unit>("Requesting more memory than available should throw an exception")
    }

    @Test
    fun testReservations() = runTest {
        val memoryManager = MemoryManager(1000)
        val reservation = memoryManager.reserve(100, this)
        Assertions.assertEquals(900, memoryManager.remainingMemoryBytes)
        reservation.release()
        Assertions.assertEquals(1000, memoryManager.remainingMemoryBytes)
    }
}
