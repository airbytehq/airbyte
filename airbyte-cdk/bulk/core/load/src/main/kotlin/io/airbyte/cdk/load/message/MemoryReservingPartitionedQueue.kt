/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.state.ReservationManager
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.runBlocking
import org.jetbrains.annotations.VisibleForTesting

class ResourceReservingPartitionedQueue<T>(
    val reservationManager: ReservationManager,
    val ratioOfTotalMemoryToReserve: Double, // 0.4
    val numConsumers: Int, // 5
    val numProducers: Int, // 2
    val expectedResourceUsagePerUnit: Long, // 20971520
    val name: String? = null
) : PartitionedQueue<T> {
    val log = KotlinLogging.logger {}

    init {
        log.info { "name : $name" }
        log.info { "ratioOfTotalMemoryToReserve : $ratioOfTotalMemoryToReserve" }
        log.info { "numConsumers : $numConsumers" }
        log.info { "numProducers : $numProducers" }
        log.info { "expectedResourceUsagePerUnit : $expectedResourceUsagePerUnit" }
        log.info { "requestedResourceAmount : $requestedResourceAmount" }
        log.info { "minNumUnits : $minNumUnits" }
        log.info { "maxMessageSize : $maxMessageSize" }
        log.info { "clampedMessageSize : $clampedMessageSize" }
        log.info { "maxNumUnits : $maxNumUnits" }
        log.info { "totalQueueCapacity : $totalQueueCapacity" }
        log.info { "queuePartitionCapacity : $queuePartitionCapacity" }
    }

    private val requestedResourceAmount =
        (ratioOfTotalMemoryToReserve * reservationManager.totalCapacityBytes)
            .toLong() // 4 gigs * 0.4 = 1638.4 // 1600000000
    private val reservation = runBlocking {
        reservationManager.reserveOrThrow(requestedResourceAmount, this)
    }
    private val minNumUnits: Int = numProducers + numConsumers * 2 // 12
    private val maxMessageSize = reservation.bytesReserved / minNumUnits // 133333333.333

    val clampedMessageSize = expectedResourceUsagePerUnit.coerceAtMost(maxMessageSize) // 20971520
    private val maxNumUnits =
        (reservation.bytesReserved / clampedMessageSize).toInt() // 76.2939453125

    private val totalQueueCapacity: Int = (maxNumUnits - (numProducers + numConsumers)) // 69

    // Our earlier calculations should ensure this is always at least 1, but
    // we'll clamp it to be safe.
    @VisibleForTesting
    val queuePartitionCapacity: Int = (totalQueueCapacity / numConsumers).coerceAtLeast(1) // 12

    private val finalCapacity: Int =
        if (queuePartitionCapacity > 1000) queuePartitionCapacity else 1000

    private val underlying =
        StrictPartitionedQueue<T>(
            (0 until numConsumers)
                .map { ChannelMessageQueue<T>(Channel(finalCapacity)) }
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
