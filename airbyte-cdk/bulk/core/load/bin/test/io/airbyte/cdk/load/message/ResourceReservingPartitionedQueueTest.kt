/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ResourceReservingPartitionedQueueTest {

    @Test
    fun `part queue respects memory available`() = runTest {
        val reservationManager = mockk<ReservationManager>(relaxed = true)
        coEvery { reservationManager.totalCapacityBytes } returns 1000
        val reservation = mockk<Reserved<ResourceReservingPartitionedQueue<Unit>>>(relaxed = true)
        coEvery { reservation.bytesReserved } returns 500
        coEvery {
            reservationManager.reserveOrThrow<ResourceReservingPartitionedQueue<Unit>>(any(), any())
        } returns reservation
        ResourceReservingPartitionedQueue<Unit>(
            reservationManager,
            0.5,
            1, // not relevant
            1, // not relevant
            1, // not relevant
        )
        coVerify {
            reservationManager.reserveOrThrow<ResourceReservingPartitionedQueue<Unit>>(500, any())
        }
    }

    @Test
    fun `part queue clamps part size if too many workers`() {
        val reservationManager = ReservationManager(1000)
        val queue =
            ResourceReservingPartitionedQueue<Unit>(
                reservationManager,
                0.8,
                3,
                5,
                100,
            )
        val clampedSize = queue.clampedMessageSize
        Assertions.assertEquals(800 / 11, clampedSize)
    }

    @Test
    fun `part queue does not clamp part size if not too many workers`() {
        val reservationManager = ReservationManager(1000)
        val queue =
            ResourceReservingPartitionedQueue<Unit>(
                reservationManager,
                0.8,
                1,
                5,
                100,
            )
        val clampedSize = queue.clampedMessageSize
        Assertions.assertEquals(100, clampedSize)
    }

    @Test
    fun `queue capacity is derived from clamped size and available memory`() {
        val reservationManager = ReservationManager(1000)
        val queue =
            ResourceReservingPartitionedQueue<Unit>(
                reservationManager,
                0.75,
                1,
                3,
                100,
            )
        Assertions.assertEquals(100L, queue.clampedMessageSize)
        Assertions.assertEquals(3, queue.queuePartitionCapacity)
    }
}
