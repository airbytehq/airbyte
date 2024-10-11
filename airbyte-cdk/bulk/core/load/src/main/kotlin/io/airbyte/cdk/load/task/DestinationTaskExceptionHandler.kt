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
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * The level at which a task operates:
 * - SyncTask: global across all streams
 * - StreamTask: affined to a single stream
 */
sealed interface LeveledTask : Task

interface SyncTask : LeveledTask

interface StreamTask : LeveledTask {
    val stream: DestinationStream
}

interface DestinationTaskExceptionHandler<T : Task> : TaskExceptionHandler<LeveledTask, T> {
    suspend fun handleSyncFailure(e: Exception)
    suspend fun handleStreamFailure(stream: DestinationStream, e: Exception)
    suspend fun handleTeardownComplete()
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
class DefaultDestinationTaskExceptionHandler(
    private val taskScopeProvider: TaskScopeProvider<ScopedTask>,
    private val catalog: DestinationCatalog,
    private val syncManager: SyncManager,
    private val failStreamTaskFactory: FailStreamTaskFactory,
    private val failSyncTaskFactory: FailSyncTaskFactory,
) : DestinationTaskExceptionHandler<ScopedTask> {
    val log = KotlinLogging.logger {}

    inner class SyncTaskWrapper(
        private val syncManager: SyncManager,
        private val innerTask: SyncTask,
    ) : SyncTask, InternalTask {
        override suspend fun execute() {
            if (!syncManager.isActive()) {
                val result = syncManager.awaitSyncResult()
                if (result is SyncSuccess) {
                    throw IllegalStateException(
                        "Task $innerTask run after sync has succeeded. This should not happen."
                    )
                }
                log.info { "Sync terminated, skipping task $innerTask." }

                return
            }

            try {
                innerTask.execute()
            } catch (e: Exception) {
                handleSyncFailure(e)
            }
        }

        override fun toString(): String {
            return "SyncTaskWrapper(innerTask=$innerTask)"
        }
    }

    inner class StreamTaskWrapper(
        private val syncManager: SyncManager,
        private val innerTask: StreamTask,
    ) : SyncTask, InternalTask {
        override suspend fun execute() {
            // Stop dispatching tasks if the stream has been killed by a failure elsewhere.
            // Specifically fail if the stream was marked succeeded: we should not be in this state.
            val streamManager = syncManager.getStreamManager(innerTask.stream.descriptor)
            if (!streamManager.isActive()) {
                val result = streamManager.awaitStreamResult()
                if (result is StreamSucceeded) {
                    throw IllegalStateException(
                        "Task $innerTask run after its stream ${innerTask.stream.descriptor} has succeeded. This should not happen."
                    )
                }
                log.info {
                    "Stream ${innerTask.stream.descriptor} terminated with $result, skipping task $innerTask."
                }
                return
            }

            try {
                innerTask.execute()
            } catch (e: Exception) {
                handleStreamFailure(innerTask.stream, e)
            }
        }

        override fun toString(): String {
            return "StreamTaskWrapper(innerTask=$innerTask)"
        }
    }

    override fun withExceptionHandling(task: LeveledTask): ScopedTask {
        return when (task) {
            is SyncTask -> SyncTaskWrapper(syncManager, task)
            is StreamTask -> SyncTaskWrapper(syncManager, StreamTaskWrapper(syncManager, task))
        }
    }

    override suspend fun handleSyncFailure(e: Exception) {
        log.error { "Sync failed: $e: killing remaining streams" }
        catalog.streams.forEach {
            val task = failStreamTaskFactory.make(this, e, it, kill = true)
            taskScopeProvider.launch(task)
        }
        val failSyncTask = failSyncTaskFactory.make(this, e)
        taskScopeProvider.launch(failSyncTask)
    }

    override suspend fun handleStreamFailure(stream: DestinationStream, e: Exception) {
        log.error { "Caught failure in stream task: $e for ${stream.descriptor}, failing stream" }
        val failStreamTask = failStreamTaskFactory.make(this, e, stream, kill = false)
        taskScopeProvider.launch(failStreamTask)
    }

    override suspend fun handleTeardownComplete() {
        taskScopeProvider.close()
    }
}
