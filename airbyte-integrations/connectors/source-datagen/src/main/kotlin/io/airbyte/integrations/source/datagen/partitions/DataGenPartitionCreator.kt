package io.airbyte.integrations.source.datagen.partitions

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.streams
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicReference

@Singleton
class DataGenPartitionCreator (
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer,
    val feedBootstrap: StreamFeedBootstrap): PartitionsCreator {

    private val acquiredThread = AtomicReference<ConcurrencyResource.AcquiredThread>()
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources() : TryAcquireResourcesStatus {
        val acquiredThread: ConcurrencyResource.AcquiredThread = concurrencyResource.tryAcquire()
            ?: return TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredThread.set(acquiredThread)
        return TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> {
        var allStreams = feedBootstrap.feed.streams
        val activeStreams: List<Stream> by lazy {
            allStreams.filter { feedBootstrap.currentState(it) != null}
        }
        val partitionReader = DataGenPartitionReader(resourceAcquirer, feedBootstrap)
        return listOf(partitionReader)
    }

    override fun releaseResources() {
        acquiredThread.getAndSet(null)?.close()
    }
}
