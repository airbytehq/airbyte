/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.util.CloseableCoroutine

interface Task {
    suspend fun execute()
}

/**
 * A TaskLauncher is responsible for starting and stopping the task workflow, and for managing
 * transitions between tasks.
 */
interface TaskLauncher {
    /**
     * Execute the task workflow. Should dispatch tasks asynchronously and suspend until the
     * workflow is complete.
     */
    suspend fun run()
}

/**
 * Wraps tasks with exception handling. It should perform all necessary exception handling, then
 * execute the provided callback.
 */
interface TaskExceptionHandler<T : Task, U : Task> {
    // Wrap a task with exception handling.
    suspend fun withExceptionHandling(task: T): U

    // Set a callback that will be invoked when any exception handling is done.
    suspend fun setCallback(callback: suspend () -> Unit)
}

/** Provides the scope(s) in which tasks run. */
interface TaskScopeProvider<T : Task> : CloseableCoroutine {
    /** Launch a task in the correct scope. */
    suspend fun launch(task: T)

    /** Unliked [close], may attempt to fail gracefully, but should guarantee return. */
    suspend fun kill()
}
