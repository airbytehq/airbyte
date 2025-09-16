package io.airbyte.integrations.source.datagen.partitionops

import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSharedState
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSourcePartition
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenStreamState
import java.util.concurrent.atomic.AtomicReference

class DataGenPartitionsCreator (
    val partition: DataGenSourcePartition,
    val partitionFactory: DataGenSourcePartitionFactory
): PartitionsCreator {

    val streamState: DataGenStreamState = partition.streamState
    val sharedState: DataGenSharedState = streamState.sharedState

    private val acquiredResources = AtomicReference<AcquiredResources?>()
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources() : TryAcquireResourcesStatus {
        val acquiredResources: AcquiredResources = sharedState.tryAcquireResourcesForCreator()
            ?: return TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> {
        val splitPartitions = partitionFactory.split(partition)
        val partitionReaders = splitPartitions.map { splitPartition -> DataGenPartitionReader(splitPartition) }
        return partitionReaders
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
