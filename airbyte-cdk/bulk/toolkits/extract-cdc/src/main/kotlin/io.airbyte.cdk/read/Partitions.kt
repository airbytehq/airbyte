/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.sync.Mutex

private class LimitedMutex(private val maxCount: Int) {
    private val mutex = Mutex()
    private var lockCount = AtomicInteger(0)

    @Synchronized
    fun canLock(): Boolean {
        return maxCount > lockCount.get()
    }

    @Synchronized
    fun tryLock(): Boolean {
        if (canLock()) {
            if (mutex.tryLock()) {
                lockCount.andIncrement
                return true
            }
        }
        return false
    }

    @Synchronized
    fun unlock() = mutex.unlock()

    val isLocked: Boolean
        get() = mutex.isLocked
}

interface CdcAware {
    fun cdcReadyToRun(): Boolean {
        return when (this) {
            is cdcResourceTaker -> {
                mutex.tryLock()
            }
            else -> {
                mutex.canLock() && mutex.isLocked.not()  // More runs left and not currently running
            }
        }
    }

    fun cdcDoneRunning(): Boolean {
        return mutex.isLocked.not() && mutex.canLock().not()
    }

    fun cdcRunEnded() = mutex.unlock()

    companion object {
        private val mutex = LimitedMutex(1)
    }
}

interface cdcResourceTaker {}
