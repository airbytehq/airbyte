/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import java.util.concurrent.atomic.AtomicReference

/**
 * Produces the single snapshot [MongoDbSnapshotPartitionReader] for a collection. Splitting a
 * collection into concurrent partitions is a later optimization; v1 reads one partition per stream.
 */
class MongoDbSnapshotPartitionsCreator(
    private val streamState: MongoDbStreamState,
) : PartitionsCreator {

    private val sharedState: MongoDbSharedState = streamState.sharedState
    private val acquiredResources = AtomicReference<AcquiredResources?>()

    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val resources: AcquiredResources =
            sharedState.tryAcquireResourcesForCreator()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> =
        listOf(MongoDbSnapshotPartitionReader(streamState))

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
