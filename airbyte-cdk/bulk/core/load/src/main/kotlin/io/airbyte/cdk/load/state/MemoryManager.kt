/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.util.CloseableCoroutine
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * Releasable reservation of memory. For large blocks (ie, from [MemoryManager.reserveRatio],
 * provides a submanager that can be used to manage allocating the reservation).
 */
class Reserved<T>(
    private val memoryManager: MemoryManager,
    val bytesReserved: Long,
    val value: T,
) : CloseableCoroutine {
    private var released = AtomicBoolean(false)

    suspend fun release() {
        if (!released.compareAndSet(false, true)) {
            return
        }
        memoryManager.release(bytesReserved)
    }

    fun getReservationManager(): MemoryManager = MemoryManager(bytesReserved)

    fun <U> replace(value: U): Reserved<U> = Reserved(memoryManager, bytesReserved, value)

    override suspend fun close() {
        release()
    }
}

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

    val remainingMemoryBytes: Long
        get() = totalMemoryBytes - usedMemoryBytes.get()

    /* Attempt to reserve memory. If enough memory is not available, waits until it is, then reserves. */
    suspend fun <T> reserveBlocking(memoryBytes: Long, reservedFor: T): Reserved<T> {
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

            return Reserved(this, memoryBytes, reservedFor)
        }
    }

    suspend fun <T> reserveRatio(ratio: Double, reservedFor: T): Reserved<T> {
        val estimatedSize = (totalMemoryBytes.toDouble() * ratio).toLong()
        return reserveBlocking(estimatedSize, reservedFor)
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
