/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamSucceeded
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.state.SyncSuccess
import io.airbyte.cdk.load.task.implementor.FailStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailSyncTaskFactory
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.CancellationException

/**
 * The level at which a task operates:
 * - SyncTask: global across all streams
 * - StreamTask: affined to a single stream
 */
sealed interface LeveledTask : Task

interface SyncLevel : LeveledTask

interface StreamLevel : LeveledTask {
    val stream: DestinationStream
}

interface DestinationTaskExceptionHandler<T : Task, U : Task> : TaskExceptionHandler<T, U> {
    suspend fun handleSyncFailure(e: Exception)
    suspend fun handleStreamFailure(stream: DestinationStream, e: Exception)
    suspend fun handleSyncFailed()
}

interface WrappedTask<T : Task> : Task {
    val innerTask: T
}

/**
 * The exception handler takes over the workflow in the event of an exception. Its contract is
 * * provide a wrapper that directs exceptions to the correct handler (by task type)
 * * close the task runner when the cleanup workflow is complete
 *
 * Handling works as follows:
 * * a failure in a sync-level task (setup/teardown) triggers a fail sync task
 * * a failure in a stream task triggers a fails stream task THEN a fail sync task
 * * the wrappers will skip tasks if the sync/stream has already failed
 */
@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
@Singleton
@Secondary
class DefaultDestinationTaskExceptionHandler<T>(
    private val taskScopeProvider: TaskScopeProvider<WrappedTask<ScopedTask>>,
    private val catalog: DestinationCatalog,
    private val syncManager: SyncManager,
    private val failStreamTaskFactory: FailStreamTaskFactory,
    private val failSyncTaskFactory: FailSyncTaskFactory,
) : DestinationTaskExceptionHandler<T, WrappedTask<ScopedTask>> where
T : LeveledTask,
T : ScopedTask {
    val log = KotlinLogging.logger {}

    val onException = AtomicReference(suspend {})
    private val failSyncTaskEnqueued = AtomicBoolean(false)

    inner class SyncTaskWrapper(
        private val syncManager: SyncManager,
        override val innerTask: ScopedTask,
    ) : WrappedTask<ScopedTask> {
        override suspend fun execute() {
            if (!syncManager.isActive()) {
                val result = syncManager.awaitSyncResult()
                if (result is SyncSuccess) {
                    throw IllegalStateException(
                        "Task $innerTask run after sync has succeeded. This should not happen."
                    )
                }
                log.info { "Sync task $innerTask skipped because sync has already failed." }
                return
            }

            try {
                innerTask.execute()
            } catch (e: CancellationException) {
                log.warn { "Sync task $innerTask was cancelled." }
                throw e
            } catch (e: Exception) {
                handleSyncFailure(e)
            }
        }

        override fun toString(): String {
            return "SyncTaskWrapper(innerTask=$innerTask)"
        }
    }

    inner class StreamTaskWrapper(
        private val stream: DestinationStream,
        private val syncManager: SyncManager,
        override val innerTask: ScopedTask,
    ) : WrappedTask<ScopedTask> {
        override suspend fun execute() {
            // Stop dispatching tasks if the stream has been killed by a failure elsewhere.
            // Specifically fail if the stream was marked succeeded: we should not be in this state.
            val streamManager = syncManager.getStreamManager(stream.descriptor)
            if (!streamManager.isActive()) {
                val result = streamManager.awaitStreamResult()
                if (result is StreamSucceeded) {
                    throw IllegalStateException(
                        "Task $innerTask run after its stream ${stream.descriptor} has succeeded. This should not happen."
                    )
                }
                log.info { "Stream task $innerTask skipped because stream has already failed." }
                return
            }

            try {
                innerTask.execute()
            } catch (e: CancellationException) {
                log.warn { "Stream task $innerTask was cancelled." }
                throw e
            } catch (e: Exception) {
                handleStreamFailure(stream, e)
            }
        }

        override fun toString(): String {
            return "StreamTaskWrapper(innerTask=$innerTask)"
        }
    }

    inner class NoHandlingWrapper(
        override val innerTask: ScopedTask,
    ) : WrappedTask<ScopedTask> {
        override suspend fun execute() {
            innerTask.execute()
        }

        override fun toString(): String {
            return "NoHandlingWrapper(innerTask=$innerTask)"
        }
    }

    override suspend fun setCallback(callback: suspend () -> Unit) {
        onException.set(callback)
    }

    override suspend fun withExceptionHandling(task: T): WrappedTask<ScopedTask> {
        return when (task) {
            is SyncLevel -> SyncTaskWrapper(syncManager, task)
            is StreamLevel -> StreamTaskWrapper(task.stream, syncManager, task)
            else -> throw IllegalArgumentException("Task without level: $task")
        }
    }

    override suspend fun handleSyncFailure(e: Exception) {
        log.error { "Sync failed: $e: killing remaining streams" }
        catalog.streams.forEach {
            val task = failStreamTaskFactory.make(this, e, it, kill = true)
            taskScopeProvider.launch(NoHandlingWrapper(task))
        }
        if (failSyncTaskEnqueued.setOnce()) {
            val failSyncTask = failSyncTaskFactory.make(this, e)
            taskScopeProvider.launch(NoHandlingWrapper(failSyncTask))
        } else {
            log.info { "Sync fail task already launched, not triggering a second one" }
        }
    }

    override suspend fun handleStreamFailure(stream: DestinationStream, e: Exception) {
        log.error { "Caught failure in stream task: $e for ${stream.descriptor}, failing stream" }
        val failStreamTask = failStreamTaskFactory.make(this, e, stream, kill = false)
        taskScopeProvider.launch(NoHandlingWrapper(failStreamTask))
    }

    override suspend fun handleSyncFailed() {
        onException.get().invoke()
    }
}
