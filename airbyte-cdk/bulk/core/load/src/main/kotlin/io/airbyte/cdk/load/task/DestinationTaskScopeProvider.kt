/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.Executors
import kotlin.system.measureTimeMillis
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull

/**
 * The scope in which a task should run
 * - [InternalScope]:
 * ```
 *       - internal to the task launcher
 *       - should not be blockable by implementor errors
 *       - killable w/o side effects
 * ```
 * - [ImplementorScope]: implemented by the destination
 * ```
 *       - calls implementor interface
 *       - should not block internal tasks (esp reading from stdin)
 *       - should complete if possible even when failing the sync
 * ```
 * - [ShutdownScope]: special case of [ImplementorScope]
 * ```
 *       - tasks that should run during shutdown
 *       - handles canceling/joining other tasks
 *       - (and so should not cancel themselves)
 * ```
 */
sealed interface ScopedTask : Task

interface InternalScope : ScopedTask

interface ImplementorScope : ScopedTask

interface ShutdownScope : ScopedTask

@Singleton
@Secondary
class DestinationTaskScopeProvider(config: DestinationConfiguration) :
    TaskScopeProvider<WrappedTask<ScopedTask>> {
    private val log = KotlinLogging.logger {}

    private val timeoutMs = config.gracefulCancellationTimeoutMs

    data class ControlScope(
        val job: Job,
        val dispatcher: CoroutineDispatcher,
        val scope: CoroutineScope = CoroutineScope(dispatcher + job)
    )

    private val internalScope = ControlScope(Job(), Dispatchers.IO)

    private val implementorScope =
        ControlScope(
            SupervisorJob(),
            Executors.newFixedThreadPool(config.maxNumImplementorTaskThreads)
                .asCoroutineDispatcher()
        )

    override suspend fun launch(task: WrappedTask<ScopedTask>) {
        when (task.innerTask) {
            is InternalScope -> internalScope.scope.launch { execute(task, "internal") }
            is ImplementorScope -> implementorScope.scope.launch { execute(task, "implementor") }
            is ShutdownScope -> implementorScope.scope.launch { execute(task, "shutdown") }
        }
    }

    private suspend fun execute(task: WrappedTask<ScopedTask>, scope: String) {
        log.info { "Launching task $task in scope $scope" }
        val elapsed = measureTimeMillis { task.execute() }
        log.info { "Task $task completed in $elapsed ms" }
    }

    override suspend fun close() {
        log.info { "Closing task scopes" }
        // Under normal operation, all tasks should be complete
        // (except things like force flush, which loop). So
        // - it's safe to force cancel the internal tasks
        // - implementor scope should join immediately
        implementorScope.job.join()
        log.info { "Implementor tasks completed, cancelling internal tasks." }
        internalScope.job.cancel()
    }

    override suspend fun kill() {
        log.info { "Killing task scopes" }

        // Give the implementor tasks a chance to fail gracefully
        withTimeoutOrNull(timeoutMs) {
            log.info {
                "Cancelled internal tasks, waiting ${timeoutMs}ms for implementor tasks to complete"
            }
            implementorScope.job.join()
            log.info { "Implementor tasks completed" }
        }
            ?: run {
                log.error { "Implementor tasks did not complete within ${timeoutMs}ms, cancelling" }
                implementorScope.job.cancel()
            }

        log.info { "Cancelling internal tasks" }
        internalScope.job.cancel()
    }
}
