/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest
class MemoryManagerTest {
    @Singleton
    @Replaces(MemoryManager::class)
    @Requires(env = ["test"])
    class MockAvailableMemoryProvider : AvailableMemoryProvider {
        override val availableMemoryBytes: Long = 1000
    }

    @Test
    fun testReserveBlocking() = runTest {
        val memoryManager = MemoryManager(MockAvailableMemoryProvider())
        val reserved = AtomicBoolean(false)

        try {
            withTimeout(5000) { memoryManager.reserveBlocking(900) }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Failed to reserve memory")
        }

        Assertions.assertEquals(100, memoryManager.remainingMemoryBytes)

        val job = launch {
            memoryManager.reserveBlocking(200)
            reserved.set(true)
        }

        memoryManager.reserveBlocking(0)
        Assertions.assertFalse(reserved.get())

        memoryManager.release(50)
        memoryManager.reserveBlocking(0)
        Assertions.assertEquals(150, memoryManager.remainingMemoryBytes)
        Assertions.assertFalse(reserved.get())

        memoryManager.release(25)
        memoryManager.reserveBlocking(0)
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
    fun testReserveBlockingMultithreaded() = runTest {
        val memoryManager = MemoryManager(MockAvailableMemoryProvider())
        withContext(Dispatchers.IO) {
            memoryManager.reserveBlocking(1000)
            Assertions.assertEquals(0, memoryManager.remainingMemoryBytes)
            val nIterations = 100000

            val jobs = (0 until nIterations).map { launch { memoryManager.reserveBlocking(10) } }

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
        val memoryManager = MemoryManager(MockAvailableMemoryProvider())
        try {
            memoryManager.reserveBlocking(1001)
        } catch (e: IllegalArgumentException) {
            return@runTest
        }
        Assertions.fail<Unit>("Requesting more memory than available should throw an exception")
    }
}
