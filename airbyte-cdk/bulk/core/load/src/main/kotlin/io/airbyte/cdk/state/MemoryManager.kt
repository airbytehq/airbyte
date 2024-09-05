/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.withLock

/**
 * Manages memory usage for the destination.
 *
 * TODO: Better initialization of available runtime memory?
 *
 * TODO: Some degree of logging/monitoring around how accurate we're actually being?
 */
@Singleton
class MemoryManager {
    private val availableMemoryBytes: Long = Runtime.getRuntime().maxMemory()
    private var usedMemoryBytes = AtomicLong(0L)
    private val memoryLock = ReentrantLock()
    private val memoryLockCondition = memoryLock.newCondition()

    suspend fun reserveBlocking(memoryBytes: Long) {
        memoryLock.withLock {
            while (usedMemoryBytes.get() + memoryBytes > availableMemoryBytes) {
                memoryLockCondition.await()
            }
            usedMemoryBytes.addAndGet(memoryBytes)
        }
    }

    suspend fun reserveRatio(ratio: Double): Long {
        val estimatedSize = (availableMemoryBytes.toDouble() * ratio).toLong()
        reserveBlocking(estimatedSize)
        return estimatedSize
    }

    fun release(memoryBytes: Long) {
        memoryLock.withLock {
            usedMemoryBytes.addAndGet(-memoryBytes)
            memoryLockCondition.signalAll()
        }
    }
}
