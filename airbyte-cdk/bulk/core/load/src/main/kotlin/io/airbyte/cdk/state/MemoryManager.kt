/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import io.airbyte.cdk.util.CloseableCoroutine
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * Manages memory usage for the destination.
 *
 * TODO: Better initialization of available runtime memory?
 *
 * TODO: Some degree of logging/monitoring around how accurate we're actually being?
 */
@Singleton
class MemoryManager(availableMemoryProvider: AvailableMemoryProvider) {
    // This is slightly awkward, but Micronaut only injects the primary constructor
    constructor(
        availableMemory: Long
    ) : this(
        object : AvailableMemoryProvider {
            override val availableMemoryBytes: Long = availableMemory
        }
    )

    private val totalMemoryBytes = availableMemoryProvider.availableMemoryBytes
    private var usedMemoryBytes = AtomicLong(0L)
    private val mutex = Mutex()
    private val syncChannel = Channel<Unit>(Channel.UNLIMITED)

    /**
     * Releasable reservation of memory. For large blocks (ie, from [reserveRatio], provides a
     * submanager that can be used to manage allocating the reservation).
     */
    inner class Reservation(val bytes: Long) : CloseableCoroutine {
        private var released = AtomicBoolean(false)

        suspend fun release() {
            if (!released.compareAndSet(false, true)) {
                return
            }
            release(bytes)
        }

        fun getReservationManager(): MemoryManager = MemoryManager(bytes)

        override suspend fun close() {
            release()
        }
    }

    val remainingMemoryBytes: Long
        get() = totalMemoryBytes - usedMemoryBytes.get()

    /* Attempt to reserve memory. If enough memory is not available, waits until it is, then reserves. */
    suspend fun reserveBlocking(memoryBytes: Long): Reservation {
        if (memoryBytes > totalMemoryBytes) {
            throw IllegalArgumentException(
                "Requested ${memoryBytes}b memory exceeds ${totalMemoryBytes}b total"
            )
        }

        mutex.withLock {
            while (usedMemoryBytes.get() + memoryBytes > totalMemoryBytes) {
                syncChannel.receive()
            }
            usedMemoryBytes.addAndGet(memoryBytes)

            return Reservation(memoryBytes)
        }
    }

    suspend fun reserveRatio(ratio: Double): Reservation {
        val estimatedSize = (totalMemoryBytes.toDouble() * ratio).toLong()
        reserveBlocking(estimatedSize)
        return Reservation(estimatedSize)
    }

    suspend fun release(memoryBytes: Long) {
        usedMemoryBytes.addAndGet(-memoryBytes)
        syncChannel.send(Unit)
    }
}

interface AvailableMemoryProvider {
    val availableMemoryBytes: Long
}

@Singleton
@Secondary
class JavaRuntimeAvailableMemoryProvider : AvailableMemoryProvider {
    override val availableMemoryBytes: Long = Runtime.getRuntime().maxMemory()
}
