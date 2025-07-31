package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.task.internal.ReservingDeserializingInputFlow
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.map

@Factory
class DataFlowPipelineInputFlow {
    @Singleton
    fun ioFlow(
        reservingFlow: ReservingDeserializingInputFlow,
    ): Flow<DataFlowStageIO> {
        return reservingFlow
            .filter { it.second.value is DestinationRecord }
            .map {
                val msg = it.second.value as DestinationRecord
                it.second.release()

                DataFlowStageIO(
                    raw = msg.asDestinationRecordRaw(),
                )
            }
    }
}
