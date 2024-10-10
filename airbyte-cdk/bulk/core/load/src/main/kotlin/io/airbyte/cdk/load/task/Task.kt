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
    suspend fun start()
}

/**
 * Wraps tasks with exception handling. It should provide an exception handling workflow and take
 * responsibility for closing scopes, etc.
 */
interface TaskExceptionHandler<T : Task, U : Task> {
    fun withExceptionHandling(task: T): U
}

/** Provides the scope(s) in which tasks run. */
interface TaskScopeProvider<T : Task> : CloseableCoroutine {
    /** Launch a task in the correct scope. */
    suspend fun launch(task: T)

    /** Unliked close, may attempt to fail gracefully, but should guarantee return. */
    suspend fun kill()
}
