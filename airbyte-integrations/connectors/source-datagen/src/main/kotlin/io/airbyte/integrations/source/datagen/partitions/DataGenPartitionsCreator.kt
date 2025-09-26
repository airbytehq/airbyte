/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.partitions

import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import java.util.concurrent.atomic.AtomicReference

class DataGenPartitionsCreator(
    val partition: DataGenSourcePartition,
    val partitionFactory: DataGenSourcePartitionFactory
) : PartitionsCreator {

    val streamState: DataGenStreamState = partition.streamState
    val sharedState: DataGenSharedState = streamState.sharedState

    private val acquiredResources = AtomicReference<AcquiredResources?>()
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources =
            sharedState.tryAcquireResourcesForCreator()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> {
        val splitPartitions = partitionFactory.split(partition)
        val partitionReaders =
            splitPartitions.map { splitPartition -> DataGenPartitionReader(splitPartition) }
        return partitionReaders
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
