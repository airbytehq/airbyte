package io.airbyte.cdk.write

import kotlinx.coroutines.channels.Channel

class WorkQueue {
    private val queue = Channel<Task>(Channel.UNLIMITED)

    companion object {
        val instance = WorkQueue()
    }

    suspend fun enqueue(task: Task) {
        queue.send(task)
    }

    suspend fun receiveMaybe(): Task? {
        return queue.receiveCatching().getOrNull()
    }

    fun isOpen(): Boolean {
        return !queue.isClosedForReceive
    }
}
