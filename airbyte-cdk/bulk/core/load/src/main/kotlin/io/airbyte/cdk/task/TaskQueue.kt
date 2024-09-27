/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Prototype
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.launch

interface Task {
    suspend fun execute()
}

/**
 * A Task is a unit of work that can be executed concurrently. Even though we aren't scheduling
 * threads or enforcing concurrency limits here, launching tasks from a queue in a dedicated scope
 * frees the caller not to have to await completion.
 *
 * TODO: Extend this to collect and report task completion.
 *
 * TODO: Set concurrency for this scope from the configuration.
 */
@Prototype
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "task is guaranteed to be non-null by Kotlin's type system"
)
class TaskQueue {
    val log = KotlinLogging.logger {}

    private val queue = Channel<Task>(Channel.UNLIMITED)

    suspend fun enqueue(task: Task) {
        queue.send(task)
    }

    suspend fun start() {
        /**
         * Start task execution in its own scope so that we can catch exceptions and flush the
         * queue.
         *
         * NOTE: We're not using a supervisor job, because we want all remaining tasks to be
         * canceled. In the future if we want to implement a custom policy (eg, invoke Task::cleanup
         * on all failed tasks), we can revisit that.
         */
        try {
            coroutineScope {
                queue.receiveAsFlow().collect { task ->
                    launch {
                        log.info { "Executing task: $task" }
                        task.execute()
                    }
                }
            }
        } catch (t: Throwable) {
            log.error { "Exception in task runner, discarding remaining tasks: $t" }
            emptyQueue()
            throw t
        }
    }

    fun close() {
        queue.close()
    }

    /**
     * This isn't strictly speaking necessary, but it would be
     * good to know what was enqueued when the failure happened.
     */
    private suspend fun emptyQueue() {
        while (true) {
            val result = queue.tryReceive()
            if (result.isFailure) {
                break
            } else if (result.isSuccess) {
                log.info { "Discarding task: ${result.getOrNull()}" }
            }
        }
    }
}
