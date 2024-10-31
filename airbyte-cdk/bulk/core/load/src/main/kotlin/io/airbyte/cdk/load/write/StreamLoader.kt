/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamIncompleteResult

/**
 * Implementor interface. The framework calls open and close once per stream at the beginning and
 * end of processing. The framework calls processRecords once per batch of records as batches of the
 * configured size become available. (Specified in @
 * [io.airbyte.cdk.command.WriteConfiguration.recordBatchSizeBytes])
 *
 * [start] is called once before any records are processed.
 *
 * [processRecords] is called whenever a batch of records is available for processing, and only
 * after [start] has returned successfully. The return value is a client-defined implementation of @
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
    suspend fun processRecords(records: Iterator<DestinationRecord>, totalSizeBytes: Long): Batch
    suspend fun processBatch(batch: Batch): Batch = SimpleBatch(Batch.State.COMPLETE)
    suspend fun close(streamFailure: StreamIncompleteResult? = null) {}
}
