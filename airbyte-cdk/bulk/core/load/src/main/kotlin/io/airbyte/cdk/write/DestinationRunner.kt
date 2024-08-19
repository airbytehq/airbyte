package io.airbyte.cdk.write

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.yield

/**
 * Runs a DestinationTask state machine, either from an arbitrary initial task
 * or by wrapping a StandardDestination in the default state machine entry point.
 */
class DestinationRunner(
    private val initialTask: AbstractDestinationTask<*, *>
) {
    constructor(destination: StandardDestination): this(
        DefaultSetup(destination)
    )

    private val log = KotlinLogging.logger {}

    // TODO: From configuration
    companion object {
        const val MAX_TASKS = 10
        const val WAIT_TIME_MS = 500L
    }

    private val catalog = DummyCatalog() // TODO: from real catalog
    private val streamComplete = mutableMapOf<Stream, Boolean>()

    private val queue = Channel<AbstractDestinationTask<*, *>>(Channel.UNLIMITED)
    private val nTasks = AtomicInteger(0)
    private val nTasksPerType = mutableMapOf<String, AtomicInteger>()
    private val nTasksPerTypePerStream = mutableMapOf<String, MutableMap<Stream, AtomicInteger>>()
    private val seenUniqueIds = mutableSetOf<String>()
    private val taskCounters = mutableMapOf<String, Int>()

    /**
     * Enqueue a task for execution.
     */
    private suspend fun enqueue(task: AbstractDestinationTask<*, *>) {
        queue.send(task)
    }

    val done = AtomicBoolean(false)
    suspend fun run() = coroutineScope {
        log.info { "Enqueueing initial task: $initialTask" }
        enqueue(initialTask)

        log.info { "Entering main task loop" }
        done.set(false)
        do {
            // Wait if we're at max concurrency
            while (nTasks.get() >= MAX_TASKS) {
                log.debug { "At max concurrency; waiting $WAIT_TIME_MS ms" }
                delay(WAIT_TIME_MS)
            }

            // Get the next task
            val task = queue.receiveCatching().getOrNull()
                ?: throw IllegalStateException("Task queue closed unexpectedly")

            // Enforce concurrency limits per type / gather counters
            val counters = mutableListOf<AtomicInteger>()
            if (task is DestinationTask<*> && task.concurrency != null) {
                val (taskId, perSync, _) = task.concurrency!!

                if (perSync > 0) {
                    val counter = nTasksPerType
                        .getOrPut(taskId) { AtomicInteger(0) }

                    if (counter.incrementAndGet() > perSync) {
                        enqueue(task)
                        val count = counter.decrementAndGet()
                        log.debug { "Re-enqueueing task $task due to per-sync concurrency guard: $taskId; $count/$perSync" }
                        continue
                    } else {
                        counters.add(counter)
                    }
                }

//                if (perStream > 0) {
//                    val counter = nTasksPerTypePerStream
//                        .getOrPut(taskId) { mutableMapOf() }
//                        .getOrPut(task.stream) { AtomicInteger(0) }
//
//                    if (counter.incrementAndGet() > perStream) {
//                        enqueue(task)
//                        val count = counter.decrementAndGet()
//                        log.debug { "Re-enqueueing task $task due to per-stream concurrency guard: $taskId; $count/$perStream" }
//                        continue
//                    } else {
//                        counters.add(counter)
//                    }
//                }
            }

            // Dispatch the task
            launch {
                nTasks.incrementAndGet()
                log.info { "Executing task: $task" }
                when (task) {
                    is ControlTask<*, *> -> {
                        task.execute().forEach { task -> enqueue(task) }
                    }
                    is DestinationTask<*> -> task.execute()
                }
                nTasks.decrementAndGet()
                counters.forEach { it.decrementAndGet() }
            }
            yield()
        } while (!done.get())
    }

    fun stop() {
        done.set(true)
    }
}
