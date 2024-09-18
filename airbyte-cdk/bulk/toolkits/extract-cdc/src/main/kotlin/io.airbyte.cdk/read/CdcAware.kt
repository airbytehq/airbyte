/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

interface CdcAware {
    fun cdcReadyToRun(): Boolean {
        return when (this) {
            // For cdc resource taker retrun try lock cdc mutex
            is CdcResourceTaker -> mutex.tryLock()
            // else return are there ore runs left and not currently running
            else -> mutex.canLock() && mutex.isLocked.not()
        }
    }

    fun isCdcDoneRunning(): Boolean {
        // Are all cdc runs done for this session
        return mutex.isLocked.not() && mutex.canLock().not()
    }

    // Release cdc mutex
    fun cdcRunEnded() = mutex.unlock()

    companion object {
        // We can currenly run cdc only once per session
        private val mutex = LimitedLockMutex(1)
    }
}
