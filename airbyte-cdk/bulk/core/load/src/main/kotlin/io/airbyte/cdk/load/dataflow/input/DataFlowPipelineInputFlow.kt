package io.airbyte.cdk.load.dataflow.input

import io.airbyte.cdk.load.message.DestinationRecord
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.message.DestinationMessage
import kotlinx.coroutines.flow.filterIsInstance

@Factory
class DataFlowPipelineInputFlow {
    @Singleton
    fun ioFlow(
        inputFlow: Flow<DestinationMessage>,
    ): Flow<DataFlowStageIO> {
        return inputFlow
            .filterIsInstance(DestinationRecord::class)
            .map {
                DataFlowStageIO(
                    raw = it.asDestinationRecordRaw(),
                )
            }
    }
}
