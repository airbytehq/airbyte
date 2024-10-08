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
import kotlinx.coroutines.supervisorScope
import kotlinx.coroutines.withTimeoutOrNull

/**
 * The scope in which a task should run
 * - InternalTask:
 * ```
 *       - internal to the task launcher
 *       - should not be blockable by implementor errors
 *       - killable w/o side effects
 * ```
 * - ImplementorTask: implemented by the destination
 * ```
 *       - calls implementor interface
 *       - should not block internal tasks (esp reading from stdin)
 *       - should complete if possible even when failing the sync
 * ```
 */
sealed interface ScopedTask : Task

interface InternalTask : ScopedTask

interface ImplementorTask : ScopedTask

@Singleton
@Secondary
class DestinationTaskScopeProvider(config: DestinationConfiguration) :
    TaskScopeProvider<ScopedTask> {
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

    override suspend fun launch(task: ScopedTask) {
        when (task) {
            is InternalTask -> internalScope.scope.launch { execute(task) }
            is ImplementorTask -> implementorScope.scope.launch { execute(task) }
        }
    }

    private suspend fun execute(task: ScopedTask) {
        log.info { "Launching task $task" }
        val elapsed = measureTimeMillis { task.execute() }
        log.info { "Task $task completed in $elapsed ms" }
    }

    override suspend fun close() = supervisorScope {
        log.info { "Closing task scopes" }
        internalScope.job.cancel()
        // Under normal operation, all tasks should be complete
        // (except things like force flush, which loop). So
        // - it's safe to force cancel the internal tasks
        // - implementor scope should join immediately unless we're
        //   failing, in which case we want to give them a chance to
        //   fail gracefully
        withTimeoutOrNull(timeoutMs) {
            log.info { "Waiting ${timeoutMs}ms for implementor tasks to complete" }
            implementorScope.job.join()
        }
            ?: run {
                log.error { "Implementor tasks did not complete within ${timeoutMs}ms, cancelling" }
                implementorScope.job.cancel()
            }
    }
}
