/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers

@Singleton
class PipelineRunner(
    private val reconciler: StateReconciler,
    val pipelines: List<DataFlowPipeline>,
) {
    private val log = KotlinLogging.logger {}

    suspend fun run() {
        log.info { "Destination Pipeline Starting..." }

        reconciler.run(CoroutineScope(Dispatchers.IO))

        try {
            pipelines.forEach { it.run() }
        } finally {
            // shutdown the reconciler regardless of success or failure, so we don't hang
            reconciler.disable()
        }

        reconciler.flushCompleteStates()

        log.info { "Destination Pipeline Completed — Successfully" }
    }
}
