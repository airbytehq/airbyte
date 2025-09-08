/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.lang.IllegalStateException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.joinAll
import kotlinx.coroutines.launch

@Singleton
class PipelineRunner(
    private val reconciler: StateReconciler,
    private val store: StateStore,
    val pipelines: List<DataFlowPipeline>,
) {
    private val log = KotlinLogging.logger {}

    suspend fun run() = coroutineScope {
        log.info { "Destination Pipeline Starting..." }
        log.info { "Running with ${pipelines.size} input streams..." }

        reconciler.run(CoroutineScope(Dispatchers.IO))

        try {
            pipelines.map { p -> launch { p.run() } }.joinAll()
            log.info { "Individual pipelines complete..." }
        } finally {
            // shutdown the reconciler regardless of success or failure, so we don't hang
            log.info { "Disabling reconciler..." }
            reconciler.disable()
        }

        log.info { "Flushing final states..." }
        reconciler.flushCompleteStates()

        log.info { "Destination Pipeline Completed — Successfully" }

        if (store.hasStates()) {
            log.info { "Unflushed states detected. Failing sync." }
            throw IllegalStateException("Sync completed, but unflushed states were detected.")
        }
    }
}
