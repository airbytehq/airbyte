/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.write.RecordMunger
import io.airbyte.integrations.destination.clickhouse_v2.write.SizedWindow

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class ClickhouseDirectLoader(
    @VisibleForTesting val munger: RecordMunger,
    @VisibleForTesting val buffer: BinaryRowInsertBuffer,
) : DirectLoader {
    private var recordCountWindow = SizedWindow(Constants.MAX_BATCH_SIZE_RECORDS)
    // the sum of serialized json bytes we've accumulated
    private var bytesWindow = SizedWindow(Constants.MAX_BATCH_SIZE_BYTES)

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val munged = munger.transformForDest(record)
        buffer.accumulate(munged)

        recordCountWindow.increment(1)
        bytesWindow.increment(record.serializedSizeBytes)

        if (bytesWindow.isComplete() || recordCountWindow.isComplete()) {
            buffer.flush()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
    }

    override suspend fun finish() = buffer.flush()

    override fun close() {}

    object Constants {
        // CH recommends 10k-100k batch sizes — since we block on IO we aim on the high side
        // to amortize the overheads.
        const val MAX_BATCH_SIZE_RECORDS = 100000L
        // To prevent undue backpressure, we try to cap the buffer size at something that will
        // safely fit in the "reserved" memory, which in practice is ~180MB.
        const val MAX_BATCH_SIZE_BYTES = 70000000L
    }
}
