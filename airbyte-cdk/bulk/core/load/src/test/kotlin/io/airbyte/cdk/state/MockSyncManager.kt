/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.state

import com.google.common.collect.Range
import com.google.common.collect.RangeSet
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.CompletableDeferred

@Singleton
@Requires(env = ["MockSyncManager", "MockDestinationCatalog"])
class MockSyncManager(catalog: DestinationCatalog) : SyncManager {
    private val mockManagers = catalog.streams.associate { it.descriptor to MockStreamManager() }
    private val streamLoaders = mutableMapOf<DestinationStream.Descriptor, StreamLoader>()

    fun addPersistedRanges(stream: DestinationStream, ranges: List<Range<Long>>) {
        mockManagers[stream.descriptor]!!.persistedRanges.addAll(ranges)
    }

    override fun getStreamManager(stream: DestinationStream.Descriptor): StreamManager {
        return mockManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    override suspend fun awaitAllStreamsClosed() {
        mockManagers.forEach { (_, manager) -> manager.awaitStreamClosed() }
    }

    override fun registerStartedStreamLoader(streamLoader: StreamLoader) {
        throw NotImplementedError()
    }

    override suspend fun getOrAwaitStreamLoader(
        stream: DestinationStream.Descriptor
    ): StreamLoader {
        return streamLoaders[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    fun mockGetOrAwaitStreamLoader(streamLoader: StreamLoader) {
        streamLoaders[streamLoader.stream.descriptor] = streamLoader
    }
}

/**
 * The only thing we really need is `areRecordsPersistedUntil`. (Technically we're emulating the @
 * [StreamManager] behavior here, since the state manager doesn't actually know what ranges are
 * closed, but less than that would make the test unrealistic.)
 */
class MockStreamManager : StreamManager {
    var persistedRanges: RangeSet<Long> = TreeRangeSet.create()
    private var batchProcessingComplete: AtomicBoolean = AtomicBoolean(false)
    val streamLatch = CompletableDeferred<Unit>()
    var countedRecords: Long = 0
    var countedEndOfStream: Long = 0
    var lastCheckpoint: Long = 0

    fun mockBatchProcessingComplete(value: Boolean = true) {
        return batchProcessingComplete.set(value)
    }

    override fun countRecordIn(): Long {
        return (countedRecords++)
    }

    override fun countEndOfStream(): Long {
        countedEndOfStream++
        return countedRecords
    }

    override fun markCheckpoint(): Pair<Long, Long> {
        val checkpoint = countedRecords
        val count = checkpoint - lastCheckpoint
        lastCheckpoint = checkpoint

        return Pair(checkpoint, count)
    }

    override fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>) {
        batch.ranges.asRanges().forEach { persistedRanges.add(it) }
    }

    override fun isBatchProcessingComplete(): Boolean {
        return batchProcessingComplete.get()
    }

    override fun areRecordsPersistedUntil(index: Long): Boolean {
        return persistedRanges.encloses(Range.closedOpen(0, index))
    }

    override fun markClosed() {
        streamLatch.complete(Unit)
    }

    override fun streamIsClosed(): Boolean {
        throw NotImplementedError()
    }

    override suspend fun awaitStreamClosed() {
        streamLatch.await()
    }
}
