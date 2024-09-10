/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.SimpleBatch
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/**
 * Implementor interface. The framework calls open and close once per stream at the beginning and
 * end of processing. The framework calls processRecords once per batch of records as batches of the
 * configured size become available. (Specified in @
 * [io.airbyte.cdk.command.WriteConfiguration.recordBatchSizeBytes]
 *
 * processBatch is called once per incomplete batch returned by either processRecords or
 * processBatch itself. See @[io.airbyte.cdk.message.Batch] for more details.
 */
interface StreamLoader {
    val stream: DestinationStream

    suspend fun open() {}
    suspend fun processRecords(records: Iterator<DestinationRecord>, totalSizeBytes: Long): Batch
    suspend fun processBatch(batch: Batch): Batch = SimpleBatch(state = Batch.State.COMPLETE)
    suspend fun close() {}
}

/**
 * Default stream loader (Not yet implemented) will process the records into a locally staged file
 * of a format specified in the configuration.
 */
class DefaultStreamLoader(
    override val stream: DestinationStream,
) : StreamLoader {
    val log = KotlinLogging.logger {}

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long
    ): Batch {
        TODO(
            "Default implementation adds airbyte metadata, maybe flattens, no-op maps, and converts to destination format"
        )
    }
}

/**
 * If you do not need to perform initialization and teardown across all streams, or if your
 * per-stream operations do not need shared global state, implement this interface instead of @
 * [Destination]. The framework will call it exactly once per stream to create instances that will
 * be used for the life cycle of the stream.
 */
interface StreamLoaderFactory {
    fun make(stream: DestinationStream): StreamLoader
}

@Singleton
@Secondary
class DefaultStreamLoaderFactory() : StreamLoaderFactory {
    override fun make(stream: DestinationStream): StreamLoader {
        TODO("See above")
    }
}
