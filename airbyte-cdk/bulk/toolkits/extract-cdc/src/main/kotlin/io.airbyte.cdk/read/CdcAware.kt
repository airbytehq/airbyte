package io.airbyte.cdk.read

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
