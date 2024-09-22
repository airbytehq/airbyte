/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import com.google.common.collect.Range
import com.google.common.collect.RangeSet
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.state.StreamManager
import io.airbyte.cdk.state.StreamsManager
import io.micronaut.context.annotation.Prototype
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named

class MockStreamManager : StreamManager {
    var persistedRanges: RangeSet<Long> = TreeRangeSet.create()
    var countedRecords: Long = 0
    var countedEndOfStream: Boolean = false
    var lastCheckpoint: Long = 0

    override fun countRecordIn(): Long {
        return countedRecords++
    }

    override fun countEndOfStream(): Long {
        return if (countedEndOfStream) {
            throw IllegalStateException("End-of-stream already counted")
        } else {
            countedEndOfStream = true
            countedRecords
        }
    }

    override fun markCheckpoint(): Pair<Long, Long> {
        val checkpoint = countedRecords
        val count = checkpoint - lastCheckpoint
        lastCheckpoint = checkpoint

        return Pair(checkpoint, count)
    }

    override fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>) {
        throw NotImplementedError()
    }

    override fun isBatchProcessingComplete(): Boolean {
        throw NotImplementedError()
    }

    override fun areRecordsPersistedUntil(index: Long): Boolean {
        return persistedRanges.encloses(Range.closedOpen(0, index))
    }

    override fun markClosed() {
        throw NotImplementedError()
    }

    override fun streamIsClosed(): Boolean {
        throw NotImplementedError()
    }

    override suspend fun awaitStreamClosed() {
        throw NotImplementedError()
    }
}

@Prototype
@Requires(env = ["MockStreamsManager"])
class MockStreamsManager(@Named("mockCatalog") catalog: DestinationCatalog) : StreamsManager {
    private val mockManagers = catalog.streams.associateWith { MockStreamManager() }

    fun addPersistedRanges(stream: DestinationStream, ranges: List<Range<Long>>) {
        mockManagers[stream]!!.persistedRanges.addAll(ranges)
    }

    override fun getManager(stream: DestinationStream): StreamManager {
        return mockManagers[stream] ?: throw IllegalArgumentException("Stream not found: $stream")
    }

    override suspend fun awaitAllStreamsClosed() {
        throw NotImplementedError()
    }
}
