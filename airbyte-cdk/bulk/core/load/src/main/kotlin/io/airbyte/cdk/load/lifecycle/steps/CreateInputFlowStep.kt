package io.airbyte.cdk.load.lifecycle.steps

import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.state.ReservationManager
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.asFlow
import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.flow.flattenMerge
import kotlinx.coroutines.flow.map

@Singleton
class CreateInputFlowStep(
    @Named("dataChannelInputFlows") private val inputFlows: Array<Flow<PipelineInputEvent>>,
    @Named("queueMemoryManager") private val memoryManager: ReservationManager,
) {
    // TODO: Tests
    @OptIn(ExperimentalCoroutinesApi::class)
    fun getInputFlow(): Flow<DestinationRecordRaw> {
        return inputFlows.asFlow()
            .flattenMerge()
            .map {
                when (it) {
                    is PipelineMessage -> {
                        memoryManager.reserve(it.value.serializedSizeBytes)
                        it.value
                    }
                    // TODO: Handle stream completed messages
                    else -> null
                }
            }
            .filterNotNull()
    }
}
