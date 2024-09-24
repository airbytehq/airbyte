/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.yield

/**
 * A Task is a unit of work that can be executed concurrently. Even though we aren't scheduling
 * threads or enforcing concurrency limits here, launching tasks from a queue in a dedicated scope
 * frees the caller not to have to await completion.
 *
 * TODO: Extend this to collect and report task completion.
 *
 * TODO: Set concurrency for this scope from the configuration.
 */
@Singleton
class TaskRunner {
    private val queue = Channel<Task>(Channel.UNLIMITED)

    suspend fun enqueue(task: Task) {
        queue.send(task)
    }

    suspend fun run() = coroutineScope {
        val log = KotlinLogging.logger {}

        while (true) {
            val task = queue.receive()

            if (task is Done) {
                log.info { "Task queue received Done() task, exiting" }
                return@coroutineScope
            }

            /** Launch the task concurrently and update counters. */
            launch {
                log.info { "Executing task: $task" }
                task.execute()
            }

            yield()
        }
    }
}
