/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read

import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator

/**
 * Plans a feed as exactly one partition: a snapshot reader for a `Stream` feed, or the
 * change-stream reader for the `Global` feed. Splitting a collection into concurrent partitions is
 * a later optimization; v1 reads one partition per feed.
 */
class MongoDbPartitionsCreator(
    private val sharedState: MongoDbSharedState,
    private val makeReader: () -> PartitionReader,
) : PartitionsCreator {

    private var acquiredResources: AutoCloseable? = null

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        acquiredResources =
            sharedState.tryAcquireResourcesForCreator()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> = listOf(makeReader())

    override fun releaseResources() {
        acquiredResources?.close()
        acquiredResources = null
    }
}

/** A [PartitionsCreator] that yields no partitions, ending its feed immediately. */
data object CreateNoPartitions : PartitionsCreator {
    override fun tryAcquireResources() = PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run(): List<PartitionReader> = emptyList()

    override fun releaseResources() {}
}
