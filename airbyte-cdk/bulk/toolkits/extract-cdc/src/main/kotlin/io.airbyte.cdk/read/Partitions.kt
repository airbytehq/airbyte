/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.sync.Mutex

/** A [Mutex] wrapper that only allows locking n times */
internal class LimitedLockMutex(maxCount: Int) {
    private val mutex = Mutex()
    private var locksLeft = AtomicInteger(maxCount)

    @Synchronized
    fun canLock(): Boolean {
        return locksLeft.get() > 0
    }

    @Synchronized
    fun tryLock(): Boolean {
        if (canLock()) {
            if (mutex.tryLock()) {
                locksLeft.andDecrement
                return true
            }
        }
        return false
    }

    @Synchronized fun unlock() = mutex.unlock()

    val isLocked: Boolean
        get() = mutex.isLocked
}

/**
 * A [CdcAware] object that is also a [CdcResourceTaker] can lock the cdc resource -
 * CdcParitionReader.
 *
 * A [CdcAware] that isn't a taker can only sense whether the resource is taken, but cannot take it
 * itself - Various partition reader that need to wait for CDC run to complete.
 */
interface CdcResourceTaker {}
