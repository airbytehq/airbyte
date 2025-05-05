/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

sealed interface TerminalCondition

data object OnEndOfSync : TerminalCondition

data object OnSyncFailureOnly : TerminalCondition

data object SelfTerminating : TerminalCondition

abstract class Task {
    abstract val terminalCondition: TerminalCondition
    open var taskLauncher: DestinationTaskLauncher? = null

    abstract suspend fun execute()
}
