/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.sync.Mutex

internal class LimitedMutex(private val maxCount: Int) {
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

interface cdcResourceTaker {}
