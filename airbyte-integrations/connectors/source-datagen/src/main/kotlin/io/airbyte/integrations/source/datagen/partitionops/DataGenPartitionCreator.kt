package io.airbyte.integrations.source.datagen.partitionops

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.streams
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSharedState
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSourcePartition
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenStreamState
import jakarta.inject.Singleton
import java.time.Clock
import java.time.LocalTime
import java.util.concurrent.atomic.AtomicReference

class DataGenPartitionCreator (
    val partition: DataGenSourcePartition,
    val partitionFactory: DataGenSourcePartitionFactory,
    val clock: Clock,
    val endTime: LocalTime
): PartitionsCreator {

    val streamState: DataGenStreamState = partition.streamState
    val stream: Stream = streamState.stream
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
        // TODO: add split()
        val partitionReader = DataGenPartitionReader(partition, clock, endTime)
        return listOf(partitionReader)
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
    }
}
