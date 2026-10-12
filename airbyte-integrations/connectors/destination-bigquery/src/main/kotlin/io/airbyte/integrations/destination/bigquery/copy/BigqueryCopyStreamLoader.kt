/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.write.StreamLoader

/** Legacy CloseStreamTask runs after all batch loads and archives have finished. */
internal class BigqueryCopyStreamLoader(
    private val delegate: StreamLoader,
    private val archive: BigqueryS3Copy,
    private val syncManager: SyncManager,
) : StreamLoader {
    override val stream: DestinationStream
        get() = delegate.stream
    override suspend fun start() = delegate.start()
    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        delegate.close(hadNonzeroRecords, streamFailure)
        if (
            streamFailure == null &&
                syncManager.getStreamManager(stream.mappedDescriptor).receivedStreamComplete()
        ) {
            archive.complete(stream)
        }
    }
}
