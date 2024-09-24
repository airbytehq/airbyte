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
import jakarta.inject.Named
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.CompletableDeferred

class MockStreamsManager(@Named("mockCatalog") catalog: DestinationCatalog) : StreamsManager {
    private val mockManagers = catalog.streams.associateWith { MockStreamManager() }

    fun addPersistedRanges(stream: DestinationStream, ranges: List<Range<Long>>) {
        mockManagers[stream]!!.persistedRanges.addAll(ranges)
    }

    override fun getManager(stream: DestinationStream): StreamManager {
        return mockManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    override suspend fun awaitAllStreamsClosed() {
        mockManagers.forEach { (_, manager) -> manager.awaitStreamClosed() }
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

    fun mockBatchProcessingComplete(value: Boolean = true) {
        return batchProcessingComplete.set(value)
    }

    override fun countRecordIn(): Long {
        throw NotImplementedError()
    }

    override fun countEndOfStream(): Long {
        throw NotImplementedError()
    }

    override fun markCheckpoint(): Pair<Long, Long> {
        throw NotImplementedError()
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
