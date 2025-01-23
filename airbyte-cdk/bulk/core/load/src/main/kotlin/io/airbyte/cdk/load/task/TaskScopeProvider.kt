/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull
import org.apache.mina.util.ConcurrentHashSet

@Singleton
class TaskScopeProvider(config: DestinationConfiguration) {
    private val log = KotlinLogging.logger {}

    private val timeoutMs = config.gracefulCancellationTimeoutMs

    private val ioScope = CoroutineScope(Dispatchers.IO)
    private val verifyCompletion = ConcurrentHashSet<Job>()
    private val killOnSyncFailure = ConcurrentHashSet<Job>()
    private val cancelAtEndOfSync = ConcurrentHashSet<Job>()

    suspend fun launch(task: Task) {
        val job =
            ioScope.launch {
                log.info { "Launching $task" }
                task.execute()
                log.info { "Task $task completed" }
            }
        when (task.terminalCondition) {
            is OnEndOfSync -> cancelAtEndOfSync.add(job)
            is OnSyncFailureOnly -> killOnSyncFailure.add(job)
            is SelfTerminating -> verifyCompletion.add(job)
        }
    }

    suspend fun close() {
        log.info { "Closing normally, canceling long-running tasks" }
        cancelAtEndOfSync.forEach { it.cancel() }

        log.info { "Verifying task completion" }
        (verifyCompletion + killOnSyncFailure).forEach {
            if (!it.isCompleted) {
                log.info { "$it incomplete, waiting $timeoutMs ms" }
                withTimeout(timeoutMs) { it.join() }
            }
        }
    }

    suspend fun kill() {
        log.info { "Failing, killing input tasks and canceling long-running tasks" }
        killOnSyncFailure.forEach { it.cancel() }
        cancelAtEndOfSync.forEach { it.cancel() }

        // Give the implementor tasks a chance to fail gracefully
        withTimeoutOrNull(timeoutMs) {
            verifyCompletion.forEach {
                log.info {
                    "Cancelled killable tasks, waiting ${timeoutMs}ms for remaining tasks to complete"
                }
                it.join()
                log.info { "Tasks completed" }
            }
        }
            ?: log.error { "Timed out waiting for tasks to complete" }
    }
}
