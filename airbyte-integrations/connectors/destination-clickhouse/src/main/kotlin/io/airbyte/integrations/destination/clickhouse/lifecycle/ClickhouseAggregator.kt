package io.airbyte.integrations.destination.clickhouse.lifecycle

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.lifecycle.operations.Aggregator
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse.write.load.BinaryRowInsertBuffer
import io.airbyte.integrations.destination.clickhouse.write.load.ClickhouseDirectLoader
import io.airbyte.integrations.destination.clickhouse.write.load.SizedWindow
import jakarta.inject.Singleton

@Singleton
class ClickhouseAggregator(
    @VisibleForTesting val buffer: BinaryRowInsertBuffer,
    @VisibleForTesting val configuredRecordCountWindow: Long?,
): Aggregator() {
    private var recordCountWindow =
        SizedWindow(configuredRecordCountWindow ?: ClickhouseDirectLoader.Constants.MAX_BATCH_SIZE_RECORDS)
    // the sum of serialized json bytes we've accumulated
    private var bytesWindow = SizedWindow(ClickhouseDirectLoader.Constants.MAX_BATCH_SIZE_BYTES)

    override fun aggregate(destinationRecord: Map<String, AirbyteValue>): AggregationStatus {
        buffer.accumulate(destinationRecord)

        recordCountWindow.increment(1)
        bytesWindow.increment(record.serializedSizeBytes)

        if (bytesWindow.isComplete() || recordCountWindow.isComplete()) {
            buffer.flush()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
    }

    override fun flush(): Boolean {
        TODO("Not yet implemented")
    }
}
