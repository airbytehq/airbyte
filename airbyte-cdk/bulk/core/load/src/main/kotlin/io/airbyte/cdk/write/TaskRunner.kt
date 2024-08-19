package io.airbyte.cdk.write

import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.yield


class TaskRunner {
    companion object {
        const val WAIT_TIME_MS = 100L
    }

    val taskCounters = mutableMapOf<String, AtomicInteger>()

    suspend fun run() = coroutineScope {
        while (WorkQueue.instance.isOpen()) {
            val task = WorkQueue.instance.receiveMaybe()
            if (task == null) {
                delay(WAIT_TIME_MS)
                continue
            }

            val counter = if (task.concurrency != null) {
                val counter = taskCounters.getOrPut(task.concurrency.id) {
                    AtomicInteger(0)
                }

                if (counter.get() >= task.concurrency.limit) {
                    WorkQueue.instance.enqueue(task)
                    yield()
                    continue
                }

                counter
            } else {
                null
            }

            launch {
                counter?.incrementAndGet()
                task.execute()
                counter?.decrementAndGet()
            }

            yield()
        }
    }
}
