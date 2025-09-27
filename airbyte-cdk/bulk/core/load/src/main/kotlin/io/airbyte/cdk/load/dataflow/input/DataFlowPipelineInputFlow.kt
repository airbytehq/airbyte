/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.StateKeyClient
import io.airbyte.cdk.load.dataflow.state.StateStore
import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector

/**
 * Takes DestinationMessages and emits DataFlowStageIO.
 *
 * Adds state ids to the input, handling the serial case where we infer the state id from a global
 * counter.
 */
class DataFlowPipelineInputFlow(
    private val inputFlow: Flow<DestinationMessage>,
    private val stateStore: StateStore,
    private val stateKeyClient: StateKeyClient,
    private val completionTracker: StreamCompletionTracker,
    private val statsStore: EmittedStatsStore,
) : Flow<DataFlowStageIO> {
    val log = KotlinLogging.logger {}

    override suspend fun collect(
        collector: FlowCollector<DataFlowStageIO>,
    ) {
        inputFlow.collect {
            when (it) {
                is CheckpointMessage -> stateStore.accept(it)
                is DestinationRecord -> {
                    // tally read count
                    statsStore.increment(it.stream.unmappedDescriptor, 1, it.serializedSizeBytes)
                    // wrap, annotate and pass to pipeline
                    val raw = it.asDestinationRecordRaw()
                    val io =
                        DataFlowStageIO(
                            raw = raw,
                            partitionKey = stateKeyClient.getPartitionKey(raw),
                        )
                    collector.emit(io)
                }
                is DestinationRecordStreamComplete -> completionTracker.accept(it)
                else -> Unit
            }
        }

        log.info { "Finished routing input." }
    }
}
