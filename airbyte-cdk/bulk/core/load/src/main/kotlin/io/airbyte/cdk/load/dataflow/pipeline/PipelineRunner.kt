/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.lang.IllegalStateException
import kotlin.coroutines.cancellation.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.cancel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.selects.select

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

        // Use parent scope so that if the parent gets canceled, the reconciler also gets canceled
        reconciler.run(this)

        val pipelineScope = CoroutineScope(coroutineContext + Job(coroutineContext[Job]))
        val firstError = CompletableDeferred<Throwable>()

        try {
            // Launch all pipelines
            val allJobs =
                pipelines.map { pipeline ->
                    pipelineScope.launch {
                        try {
                            pipeline.run()
                        } catch (e: CancellationException) {
                            throw e
                        } catch (t: Throwable) {
                            firstError.complete(t)
                            throw t
                        }
                    }
                }

            // Create a deferred that completes when all jobs are done
            val allComplete = pipelineScope.async { allJobs.forEach { it.join() } }

            // Wait for EITHER first error OR all complete
            select {
                firstError.onAwait { error ->
                    log.error(error) { "Pipeline failed" }
                    pipelineScope.cancel(CancellationException("Pipeline failed", error))
                    throw error
                }
                allComplete.onAwait { log.info { "All pipelines completed successfully" } }
            }
        } finally {
            pipelineScope.cancel()
            log.info { "Disabling reconciler..." }
            reconciler.disable()
        }

        // Success path
        log.info { "Flushing final states..." }
        reconciler.flushCompleteStates()

        log.info { "Destination Pipeline Completed — Successfully" }

        if (store.hasStates()) {
            log.info { "Unflushed states detected. Failing sync." }
            throw IllegalStateException("Sync completed, but unflushed states were detected.")
        }
    }
}
