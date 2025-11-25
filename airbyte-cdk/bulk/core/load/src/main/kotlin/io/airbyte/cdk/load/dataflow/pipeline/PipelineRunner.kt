/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.config.ConnectorInputStreams
import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.lang.IllegalStateException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExecutorCoroutineDispatcher
import kotlinx.coroutines.cancel
import kotlinx.coroutines.joinAll
import kotlinx.coroutines.launch

/**
 * Orchestrates the running of pipelines in parallel, handles and propagates errors and manages the
 * state reconciler lifecycle.
 */
@Singleton
class PipelineRunner(
    private val reconciler: StateReconciler,
    private val store: StateStore,
    private val pipelines: List<DataFlowPipeline>,
    private val inputStreams: ConnectorInputStreams,
    @Named("pipelineRunnerScope") private val pipelineScope: CoroutineScope,
    @Named("aggregationDispatcher") private val aggregationDispatcher: CoroutineDispatcher,
) {
    private val log = KotlinLogging.logger {}

    private var terminalException: Throwable? = null

    suspend fun run() {
        log.info { "Destination Pipeline Starting..." }

        log.info { "Starting state reconciler..." }
        reconciler.run()

        log.info { "Starting ${pipelines.size} pipelines..." }
        pipelines.map { p -> pipelineScope.launch(exceptionHandler) { p.run() } }.joinAll()
        log.info { "Individual pipelines complete..." }

        // shutdown the reconciler regardless of success or failure, so we don't hang
        try {
            log.info { "Disabling state reconciler..." }
            reconciler.disable()
        } finally {
            if (aggregationDispatcher is ExecutorCoroutineDispatcher) {
                aggregationDispatcher.close()
            }
        }

        terminalException?.let {
            log.error(terminalException) { "Destination Pipeline Completed — Exceptionally" }
            throw it
        }

        log.info { "Flushing final states..." }
        reconciler.flushCompleteStates()

        if (store.hasStates()) {
            val stateException =
                IllegalStateException("Sync completed, but unflushed states were detected.")
            store.logStateInfo()
            log.error { "Destination Pipeline Completed — Exceptionally: $stateException" }
            throw stateException
        }

        log.info { "Destination Pipeline Completed — Successfully" }
    }

    // ensure all pipelines close when a single pipeline throws an exception
    private val exceptionHandler = CoroutineExceptionHandler { context, exception ->
        log.error { "Caught Pipeline Exception: $exception\n Cancelling Destination Pipeline..." }
        // close each input stream to cancel any blocking reads on them that would prevent shutdown
        inputStreams.closeAll()
        context.cancel()
        // capture the child exception to re-throw (core-CDK relies on catching thrown exceptions)
        // exceptions directly thrown from within this block will be suppressed
        terminalException = exception
    }
}
