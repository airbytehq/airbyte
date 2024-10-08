/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.state.StreamIncompleteResult

/**
 * Implementor interface. The framework calls open and close once per stream at the beginning and
 * end of processing. The framework calls processRecords once per batch of records as batches of the
 * configured size become available. (Specified in @
 * [io.airbyte.cdk.command.WriteConfiguration.recordBatchSizeBytes])
 *
 * [start] is called once before any records are processed.
 *
 * [processStagedLocalFile] is called once per staged local file before any records are processed,
 * and only after [start] has returned successfully. The default implementation is to return the
 * input unchanged. Implementors may override this if they want to process the file directly.
 * Otherwise, process records will be called with an iterator over the records in the file.
 *
 * [processRecords] is called whenever [processStagedLocalFile] returns the local file unchanged.
 * [Batch] that the framework may pass to [processBatch] and/or [finalize]. (See @[Batch] for more
 * details.)
 *
 * [processBatch] is called once per incomplete batch returned by either [processRecords] or
 * [processBatch] itself.
 *
 * [finalize] is called once after all records and batches have been processed successfully.
 *
 * [close] is called once after all records have been processed, regardless of success or failure.
 * If there are failed batches, they are passed in as an argument.
 */
interface StreamLoader {
    val stream: DestinationStream

    suspend fun start() {}
    suspend fun processStagedLocalFile(localFile: SpilledRawMessagesLocalFile): Batch = localFile
    suspend fun processRecords(records: Iterator<DestinationRecord>, totalSizeBytes: Long): Batch =
        throw NotImplementedError(
            "processRecords must be implemented if processStagedLocalFile is not overridden"
        )
    suspend fun processBatch(batch: Batch): Batch = SimpleBatch(Batch.State.COMPLETE)
    suspend fun close(streamFailure: StreamIncompleteResult? = null) {}
}
