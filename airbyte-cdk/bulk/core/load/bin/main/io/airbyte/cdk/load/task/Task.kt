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
