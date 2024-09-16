/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
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
class MemoryManager(private val availableMemoryProvider: AvailableMemoryProvider) {
    private val totalMemoryBytes: Long = availableMemoryProvider.availableMemoryBytes
    private var usedMemoryBytes = AtomicLong(0L)
    private val mutex = Mutex()
    private val syncChannel = Channel<Unit>(Channel.UNLIMITED)

    val remainingMemoryBytes: Long
        get() = totalMemoryBytes - usedMemoryBytes.get()

    /* Attempt to reserve memory. If enough memory is not available, waits until it is, then reserves. */
    suspend fun reserveBlocking(memoryBytes: Long) {
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
        }
    }

    suspend fun reserveRatio(ratio: Double): Long {
        val estimatedSize = (totalMemoryBytes.toDouble() * ratio).toLong()
        reserveBlocking(estimatedSize)
        return estimatedSize
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
