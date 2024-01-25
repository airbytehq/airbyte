package io.airbyte.integrations.base.destination.typing_deduping

import java.util.concurrent.TimeUnit
import java.util.concurrent.locks.Condition
import java.util.concurrent.locks.Lock

class NoOpRawTableTDLock: Lock {
    override fun lock() {}

    override fun lockInterruptibly() {}

    override fun tryLock(): Boolean {
        // To mimic NoOp behavior always return true that lock is acquired
        return true
    }

    override fun tryLock(time: Long, unit: TimeUnit): Boolean {
        return tryLock()
    }

    override fun unlock() {}

    override fun newCondition(): Condition {
        // Always throw exception to avoid callers from using this path
        throw UnsupportedOperationException("This lock implementation does not support retrieving a Condition")
    }
}
