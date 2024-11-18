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

class ReservationManagerTest {
    @Test
    fun testReserve() = runTest {
        val manager = ReservationManager(1000)
        val reserved = AtomicBoolean(false)

        try {
            withTimeout(5000) { manager.reserve(900, this) }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Failed to reserve memory")
        }

        Assertions.assertEquals(100, manager.remainingCapacityBytes)

        val job = launch {
            manager.reserve(200, this)
            reserved.set(true)
        }

        manager.reserve(0, this)
        Assertions.assertFalse(reserved.get())

        manager.release(50)
        manager.reserve(0, this)
        Assertions.assertEquals(150, manager.remainingCapacityBytes)
        Assertions.assertFalse(reserved.get())

        manager.release(25)
        manager.reserve(0, this)
        Assertions.assertEquals(175, manager.remainingCapacityBytes)
        Assertions.assertFalse(reserved.get())

        manager.release(25)
        try {
            withTimeout(5000) { job.join() }
        } catch (e: Exception) {
            Assertions.fail<Unit>("Failed to unblock reserving memory")
        }
        Assertions.assertEquals(0, manager.remainingCapacityBytes)
        Assertions.assertTrue(reserved.get())
    }

    @Test
    fun testReserveMultithreaded() = runTest {
        val manager = ReservationManager(1000)
        withContext(Dispatchers.IO) {
            manager.reserve(1000, this)
            Assertions.assertEquals(0, manager.remainingCapacityBytes)
            val nIterations = 100000

            val jobs = (0 until nIterations).map { launch { manager.reserve(10, this) } }

            repeat(nIterations) {
                manager.release(10)
                Assertions.assertTrue(
                    manager.remainingCapacityBytes >= 0,
                    "Remaining memory is negative: ${manager.remainingCapacityBytes}"
                )
            }
            jobs.forEach { it.join() }
            Assertions.assertEquals(0, manager.remainingCapacityBytes)
        }
    }

    @Test
    fun testRequestingMoreThanAvailableThrows() = runTest {
        val manager = ReservationManager(1000)
        try {
            manager.reserve(1001, this)
        } catch (e: IllegalArgumentException) {
            return@runTest
        }
        Assertions.fail<Unit>("Requesting more memory than available should throw an exception")
    }

    @Test
    fun testReservations() = runTest {
        val manager = ReservationManager(1000)
        val reservation = manager.reserve(100, this)
        Assertions.assertEquals(900, manager.remainingCapacityBytes)
        reservation.release()
        Assertions.assertEquals(1000, manager.remainingCapacityBytes)
    }
}
