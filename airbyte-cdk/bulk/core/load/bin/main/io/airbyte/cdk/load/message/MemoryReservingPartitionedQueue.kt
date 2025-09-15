/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.state.ReservationManager
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.runBlocking
import org.jetbrains.annotations.VisibleForTesting

class ResourceReservingPartitionedQueue<T>(
    val reservationManager: ReservationManager,
    val ratioOfTotalMemoryToReserve: Double,
    val numConsumers: Int,
    val numProducers: Int,
    val expectedResourceUsagePerUnit: Long
) : PartitionedQueue<T> {

    private val requestedResourceAmount =
        (ratioOfTotalMemoryToReserve * reservationManager.totalCapacityBytes).toLong()
    private val reservation = runBlocking {
        reservationManager.reserveOrThrow(requestedResourceAmount, this)
    }
    private val minNumUnits: Int = numProducers + numConsumers * 2
    private val maxMessageSize = reservation.bytesReserved / minNumUnits

    val clampedMessageSize = expectedResourceUsagePerUnit.coerceAtMost(maxMessageSize)
    private val maxNumUnits = (reservation.bytesReserved / clampedMessageSize).toInt()

    private val totalQueueCapacity: Int = (maxNumUnits - (numProducers + numConsumers))

    // Our earlier calculations should ensure this is always at least 1, but
    // we'll clamp it to be safe.
    @VisibleForTesting
    val queuePartitionCapacity: Int = (totalQueueCapacity / numConsumers).coerceAtLeast(1)

    private val underlying =
        StrictPartitionedQueue<T>(
            (0 until numConsumers)
                .map { ChannelMessageQueue<T>(Channel(queuePartitionCapacity)) }
                .toTypedArray()
        )

    override val partitions: Int = numConsumers

    override fun consume(partition: Int): Flow<T> = underlying.consume(partition)

    override suspend fun close() {
        underlying.close()
        reservation.release()
    }

    override suspend fun broadcast(value: T) = underlying.broadcast(value)

    override suspend fun publish(value: T, partition: Int) = underlying.publish(value, partition)
}
