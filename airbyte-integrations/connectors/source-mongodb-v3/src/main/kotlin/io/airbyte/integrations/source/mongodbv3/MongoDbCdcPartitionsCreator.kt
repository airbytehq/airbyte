/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import java.util.concurrent.atomic.AtomicReference

/** Produces the single change-stream [MongoDbCdcPartitionReader] for the `Global` feed. */
class MongoDbCdcPartitionsCreator(
    private val sharedState: MongoDbSharedState,
    private val feedBootstrap: GlobalFeedBootstrap,
) : PartitionsCreator {

    private val acquiredResources = AtomicReference<CreatorAcquiredResources?>()

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val resources: CreatorAcquiredResources =
            sharedState.tryAcquireResourcesForCreator()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> =
        listOf(MongoDbCdcPartitionReader(sharedState, feedBootstrap))

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
