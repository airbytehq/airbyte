/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlin.system.measureTimeMillis
import kotlinx.coroutines.CompletableJob
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
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
 */
sealed interface ScopedTask : Task

interface InternalScope : ScopedTask

interface ImplementorScope : ScopedTask

/**
 * Some tasks should be immediately cancelled upon any failure (for example, reading from stdin, the
 * every-15-minutes flush). Those tasks should be placed into the fail-fast scope.
 */
interface KillableScope : ScopedTask

interface WrappedTask<T : Task> : Task {
    val innerTask: T
}

@Singleton
@Secondary
class TaskScopeProvider(config: DestinationConfiguration) {
    private val log = KotlinLogging.logger {}

    private val timeoutMs = config.gracefulCancellationTimeoutMs

    data class ControlScope(
        val name: String,
        val job: CompletableJob,
        val dispatcher: CoroutineDispatcher
    ) {
        val scope: CoroutineScope = CoroutineScope(dispatcher + job)
        val runningJobs: AtomicLong = AtomicLong(0)
    }

    private val internalScope = ControlScope("internal", Job(), Dispatchers.IO)

    private val implementorScope =
        ControlScope(
            "implementor",
            Job(),
            Executors.newFixedThreadPool(config.maxNumImplementorTaskThreads)
                .asCoroutineDispatcher()
        )

    private val failFastScope = ControlScope("input", Job(), Dispatchers.IO)

    suspend fun launch(task: WrappedTask<ScopedTask>) {
        val scope =
            when (task.innerTask) {
                is InternalScope -> internalScope
                is ImplementorScope -> implementorScope
                is KillableScope -> failFastScope
            }
        scope.scope.launch {
            var nJobs = scope.runningJobs.incrementAndGet()
            log.info { "Launching task $task in scope ${scope.name} ($nJobs now running)" }
            val elapsed = measureTimeMillis { task.execute() }
            nJobs = scope.runningJobs.decrementAndGet()
            log.info { "Task $task completed in $elapsed ms ($nJobs now running)" }
        }
    }

    suspend fun close() {
        // Under normal operation, all tasks should be complete
        // (except things like force flush, which loop). So
        // - it's safe to force cancel the internal tasks
        // - implementor scope should join immediately
        log.info { "Closing task scopes (${implementorScope.runningJobs.get()} remaining)" }
        val uncaughtExceptions = AtomicReference<Throwable>()
        implementorScope.job.children.forEach {
            it.invokeOnCompletion { cause ->
                if (cause != null) {
                    log.error { "Uncaught exception in implementor task: $cause" }
                    uncaughtExceptions.set(cause)
                }
            }
        }
        implementorScope.job.complete()
        implementorScope.job.join()
        if (uncaughtExceptions.get() != null) {
            throw IllegalStateException(
                "Uncaught exceptions in implementor tasks",
                uncaughtExceptions.get()
            )
        }
        log.info {
            "Implementor tasks completed, cancelling internal tasks (${internalScope.runningJobs.get()} remaining)."
        }
        internalScope.job.cancel()
    }

    suspend fun kill() {
        log.info { "Killing task scopes" }
        // Terminate tasks which should be immediately terminated
        failFastScope.job.cancel()

        // Give the implementor tasks a chance to fail gracefully
        withTimeoutOrNull(timeoutMs) {
            log.info {
                "Cancelled internal tasks, waiting ${timeoutMs}ms for implementor tasks to complete"
            }
            implementorScope.job.complete()
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
