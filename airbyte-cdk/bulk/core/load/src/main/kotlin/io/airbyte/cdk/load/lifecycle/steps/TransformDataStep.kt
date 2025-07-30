package io.airbyte.cdk.load.lifecycle.steps

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking

/**
 * Transform a raw record in a formatted record
 */
@Singleton
class TransformDataStep(
    private val recordMunger: RecordMungingStep,
    // private val syncManager: SyncManager,
) {
    data class MungedRecordWrapper(
        val stream: DestinationStream,
        val mungedRecord: Map<String, AirbyteValue>
    )

    fun transformData(dataFlow: Flow<DestinationRecordRaw>): Flow<MungedRecordWrapper> {
        return runBlocking {
            return@runBlocking dataFlow.map {
                MungedRecordWrapper(it.stream, recordMunger.transformForDest(it))
            }
        }
    }
}
