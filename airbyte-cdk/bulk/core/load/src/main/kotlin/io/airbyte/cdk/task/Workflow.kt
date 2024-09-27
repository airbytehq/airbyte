/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

/**
 * A [Workflow] is responsible for starting
 * transitions between tasks.
 */
interface Workflow {
    val taskRunner: TaskQueue

    suspend fun start()
    suspend fun stop() {
        taskRunner.close()
    }
}

interface WorkflowFactory<T: Workflow> {
    fun make(taskRunner: TaskQueue): T
}
