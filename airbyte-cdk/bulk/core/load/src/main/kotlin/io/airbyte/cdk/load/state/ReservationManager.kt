/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.util.CloseableCoroutine
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/** Releasable reservation of memory. */
class Reserved<T>(
    private val parentManager: ReservationManager? = null,
    val bytesReserved: Long = 0,
    val value: T,
) : CloseableCoroutine {
    private var released = AtomicBoolean(false)

    suspend fun release() {
        if (!released.compareAndSet(false, true)) {
            return
        }
        parentManager?.release(bytesReserved)
    }

    fun <U> replace(value: U): Reserved<U> = Reserved(parentManager, bytesReserved, value)

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
class ReservationManager(val totalCapacityBytes: Long) {

    private var usedBytes = AtomicLong(0L)
    private var updateChannel = MutableStateFlow(0L)
    private val reserveLock = Mutex()

    val remainingCapacityBytes: Long
        get() = totalCapacityBytes - usedBytes.get()
    val totalBytesReserved: Long
        get() = usedBytes.get()

    /* Attempt to reserve memory. If enough memory is not available, waits until it is, then reserves. */
    suspend fun <T> reserve(bytes: Long, reservedFor: T): Reserved<T> {
        reserve(bytes)

        return Reserved(this, bytes, reservedFor)
    }

    /* Attempt to reserve memory. If enough memory is not available, waits until it is, then reserves. */
    suspend fun reserve(bytes: Long) {
        if (bytes > totalCapacityBytes) {
            throw IllegalArgumentException(
                "Requested ${bytes}b exceeds ${totalCapacityBytes}b total"
            )
        }

        reserveLock.withLock {
            while (usedBytes.get() + bytes > totalCapacityBytes) {
                updateChannel.first()
            }
            usedBytes.addAndGet(bytes)
        }
    }

    suspend fun release(bytes: Long) {
        updateChannel.value = usedBytes.addAndGet(-bytes)
    }
}
