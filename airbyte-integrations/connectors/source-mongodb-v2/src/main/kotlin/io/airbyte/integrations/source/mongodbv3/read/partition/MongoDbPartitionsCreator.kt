/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.partition

import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbSharedState

/** Plans a feed as exactly one partition (splitting a collection is a later optimization). */
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
