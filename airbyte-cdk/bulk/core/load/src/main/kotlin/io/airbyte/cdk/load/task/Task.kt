/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

sealed interface TerminalCondition

data object OnEndOfSync : TerminalCondition

data object OnSyncFailureOnly : TerminalCondition

data object SelfTerminating : TerminalCondition

interface Task {
    val terminalCondition: TerminalCondition

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
