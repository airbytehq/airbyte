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
import kotlinx.coroutines.cancel
import kotlinx.coroutines.coroutineScope
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

        // Use parent scope so that if the parent gets canceled, the reconciler also gets canceled
        reconciler.run(this)

        // Create a scope that inherits from parent but allows independent cancellation
        // Using Job() instead of SupervisorJob() to allow parent cancellation to propagate
        val pipelineScope = CoroutineScope(coroutineContext + Job(coroutineContext[Job]))

        // Deferred to signal when all pipelines should be cancelled due to an error
        val cancellationSignal = CompletableDeferred<Throwable>()

        try {
            // Launch all pipelines concurrently
            val jobs =
                pipelines.map { pipeline ->
                    pipelineScope.launch {
                        try {
                            pipeline.run()
                        } catch (e: CancellationException) {
                            // Re-throw cancellation to properly propagate it
                            throw e
                        } catch (t: Throwable) {
                            // Signal first failure to trigger cancellation of other pipelines
                            // tryComplete returns false if already completed, avoiding races
                            if (cancellationSignal.complete(t)) {
                                log.error(t) {
                                    "Pipeline ${pipeline} failed, cancelling other pipelines"
                                }
                            }
                            throw t
                        }
                    }
                }

            // Launch a coroutine to monitor for cancellation signal
            val cancellationMonitor = launch {
                try {
                    val error = cancellationSignal.await()
                    // Cancel all pipeline jobs when error occurs
                    pipelineScope.cancel(CancellationException("Pipeline failed", error))
                } catch (e: CancellationException) {
                    // Parent scope cancelled, propagate to pipeline scope
                    pipelineScope.cancel(CancellationException("Parent scope cancelled", e))
                }
            }

            // Wait for all pipelines to complete
            jobs.forEach { job ->
                try {
                    job.join()
                } catch (e: CancellationException) {
                    // Expected when pipelines are cancelled
                    log.debug { "Pipeline cancelled: ${e.message}" }
                }
            }

            // Cancel the monitor if all pipelines completed successfully
            cancellationMonitor.cancel()

            // Check if there was an error
            if (cancellationSignal.isCompleted) {
                throw cancellationSignal.await()
            }

            log.info { "Individual pipelines complete..." }
        } finally {
            // Ensure pipeline scope is cancelled to clean up any remaining coroutines
            pipelineScope.cancel()

            // shutdown the reconciler regardless of success or failure, so we don't hang
            log.info { "Disabling reconciler..." }
            reconciler.disable()
        }

        // Only reached on success path - all pipelines completed without errors
        log.info { "Flushing final states..." }
        reconciler.flushCompleteStates()

        log.info { "Destination Pipeline Completed — Successfully" }

        if (store.hasStates()) {
            log.info { "Unflushed states detected. Failing sync." }
            throw IllegalStateException("Sync completed, but unflushed states were detected.")
        }
    }
}
