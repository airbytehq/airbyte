package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw

interface BatchLoadStrategy: LoadStrategy {
    val targetBatchSizeBytes: Long
    val maxMemoryRatioToReserveForBatches: Double

    suspend fun loadBatch(
        stream: DestinationStream.Descriptor,
        partition: Int,
        batch: Iterable<DestinationRecordRaw>
    )
}
