/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask

interface LoadPipelineStep {
    val numWorkers: Int
    fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *>
}

/**
 * Used internally by the pipeline to assemble a launcher for any loader's pipeline. CDK devs can
 * use this to implement new flavors of interface. Connector devs should generally avoid using this.
 */
abstract class LoadPipeline(
    private val steps: List<LoadPipelineStep>,
) {
    suspend fun start(launcher: suspend (Task) -> Unit) {
        steps.forEach { step -> repeat(step.numWorkers) { launcher(step.taskForPartition(it)) } }
    }

    /** For closing intermediate queues or other resources. */
    open suspend fun stop() {}
}
