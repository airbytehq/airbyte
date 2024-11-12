/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.util.CloseableCoroutine
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/** Releasable reservation of memory. */
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
class MemoryManager(val totalMemoryBytes: Long) {

    private var usedMemoryBytes = AtomicLong(0L)
    private val mutex = Mutex()
    private val syncChannel = Channel<Unit>(Channel.UNLIMITED)

    val remainingMemoryBytes: Long
        get() = totalMemoryBytes - usedMemoryBytes.get()

    /* Attempt to reserve memory. If enough memory is not available, waits until it is, then reserves. */
    suspend fun <T> reserve(memoryBytes: Long, reservedFor: T): Reserved<T> {
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

    suspend fun release(memoryBytes: Long) {
        usedMemoryBytes.addAndGet(-memoryBytes)
        syncChannel.send(Unit)
    }
}
