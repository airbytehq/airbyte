/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.dataflow.aggregate.AggregateStore
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope

class PipelineCompletionHandler(
    private val aggStore: AggregateStore,
    private val stateHistogramStore: StateHistogramStore,
) {
    private val log = KotlinLogging.logger {}

    suspend fun apply(
        cause: Throwable?,
    ) = coroutineScope {
        if (cause != null) {
            log.error { "Destination Pipeline Completed — Exceptionally" }
            throw cause
        }

        val remainingAggregates = aggStore.getAll()

        log.info { "Flushing ${remainingAggregates.size} final aggregates..." }
        remainingAggregates
            .map {
                async {
                    it.value.flush()
                    stateHistogramStore.acceptFlushedCounts(it.partitionHistogram)
                }
            }
            .awaitAll()

        log.info { "Final aggregates flushed." }
    }
}
