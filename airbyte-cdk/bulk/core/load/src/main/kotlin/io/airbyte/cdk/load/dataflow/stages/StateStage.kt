/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.StateHistogramStore
import io.airbyte.cdk.load.dataflow.state.stats.StreamStatsStore
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("state")
@Singleton
class StateStage(
    private val stateHistogramStore: StateHistogramStore,
    private val streamStatsStore: StreamStatsStore,
) : DataFlowStage {
    private val log = KotlinLogging.logger {}

    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val countUpdates = input.partitionCountsHistogram!!
        val byteUpdates = input.partitionBytesHistogram!!

        stateHistogramStore.acceptFlushedCounts(countUpdates)
        stateHistogramStore.acceptFlushedBytes(byteUpdates)
        streamStatsStore.acceptStats(input.mappedDesc!!, countUpdates, byteUpdates)

        return input
    }
}
