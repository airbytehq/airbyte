/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.StateKeyClient
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector

/**
 * Takes DestinationMessages and emits DataFlowStageIO.
 *
 * Adds state ids to the input, handling the serial case where we infer the
 * state id from a global counter.
 */
@Singleton
class DataFlowPipelineInputFlow(
    val inputFlow: Flow<DestinationMessage>,
    val stateKeyClient: StateKeyClient,
): Flow<DataFlowStageIO> {
    override suspend fun collect(
        collector: FlowCollector<DataFlowStageIO>,
    ) {
        inputFlow.collect {
            when (it) {
                is CheckpointMessage -> stateKeyClient.acceptState(it)
                is DestinationRecord -> {
                    val raw = it.asDestinationRecordRaw()
                    val io = DataFlowStageIO(
                        raw = raw,
                        stateKey = stateKeyClient.getKey(raw)
                    )
                    collector.emit(io)
                }
                else -> Unit
            }
        }
    }
}
