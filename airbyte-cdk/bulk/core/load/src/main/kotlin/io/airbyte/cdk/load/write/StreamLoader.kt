/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamProcessingFailed

/**
 * Implementor interface.
 *
 * [start] is called once before any records are processed.
 *
 * [processRecords] is called whenever a batch of records is available for processing (of the size
 * configured in [io.airbyte.cdk.load.command.DestinationConfiguration.recordBatchSizeBytes]) and
 * only after [start] has returned successfully. The return value is a client-defined implementation
 * of @ [Batch] that the framework may pass to [processBatch]. (See @[Batch] for more details.)
 *
 * [processRecords] may be called concurrently by multiple workers, so it should be thread-safe if
 * [io.airbyte.cdk.load.command.DestinationConfiguration.numProcessRecordsWorkers] > 1. For a
 * non-thread-safe alternative, use [createBatchAccumulator].
 *
 * [createBatchAccumulator] returns an optional new instance of a [BatchAccumulator] to use for
 * record processing instead of this stream loader. By default, it returns a reference to the stream
 * loader itself. Use this interface if you want each record processing worker to use a separate
 * instance (with its own state, etc).
 *
 * [processBatch] is called once per incomplete batch returned by either [processRecords] or
 * [processBatch] itself. It must be thread-safe if
 * [io.airbyte.cdk.load.command.DestinationConfiguration.numProcessBatchWorkers] > 1. If
 * [processRecords] never returns a non-[Batch.State.COMPLETE] batch, [processBatch] will never be
 * called.
 *
 * NOTE: even if [processBatch] returns a not-[Batch.State.COMPLETE] batch, it will be called again.
 * TODO: allow the client to specify subsequent processing stages instead.
 *
 * [close] is called once after all records have been processed, regardless of success or failure,
 * but only if [start] returned successfully. If any exception was thrown during processing, it is
 * passed as an argument to [close].
 */
interface StreamLoader : BatchAccumulator, FileBatchAccumulator {
    val stream: DestinationStream

    suspend fun start() {}

    suspend fun createBatchAccumulator(): BatchAccumulator = this
    suspend fun createFileBatchAccumulator(
        outputQueue: MultiProducerChannel<BatchEnvelope<*>>,
    ): FileBatchAccumulator = this

    suspend fun processBatch(batch: Batch): Batch = SimpleBatch(Batch.State.COMPLETE)
    suspend fun close(streamFailure: StreamProcessingFailed? = null) {}
}

interface BatchAccumulator {
    suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean = false
    ): Batch =
        throw NotImplementedError(
            "processRecords must be implemented if createBatchAccumulator is overridden"
        )
}

interface FileBatchAccumulator {
    /**
     * This is an unusal way to process a message (the DestinationFile). The batch are pushed to the
     * queue immediately instead of being return by the method, the main reason is that we nned to
     * keep a single instance of a PartFactory for the whole file.
     */
    suspend fun processFilePart(file: DestinationFile, index: Long): Unit =
        throw NotImplementedError(
            "processRecords must be implemented if createBatchAccumulator is overridden"
        )
}
