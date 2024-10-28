/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.CheckpointMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Inject
import jakarta.inject.Singleton

@Singleton
@Requires(env = ["MockCheckpointManager"])
class MockCheckpointManager : CheckpointManager<DestinationStream.Descriptor, CheckpointMessage> {
    @Inject lateinit var timeProvider: TimeProvider

    val streamStates =
        mutableMapOf<DestinationStream.Descriptor, MutableList<Pair<Long, CheckpointMessage>>>()
    val globalStates =
        mutableListOf<Pair<List<Pair<DestinationStream.Descriptor, Long>>, CheckpointMessage>>()

    val flushedAtMs = mutableListOf<Long>()
    var mockCheckpointIndexes = mutableMapOf<DestinationStream.Descriptor, Long>()
    var mockLastFlushTimeMs = 0L
    var maxNumFlushAttempts = 0

    override suspend fun addStreamCheckpoint(
        key: DestinationStream.Descriptor,
        index: Long,
        checkpointMessage: CheckpointMessage
    ) {
        streamStates.getOrPut(key) { mutableListOf() }.add(index to checkpointMessage)
    }

    override suspend fun addGlobalCheckpoint(
        keyIndexes: List<Pair<DestinationStream.Descriptor, Long>>,
        checkpointMessage: CheckpointMessage
    ) {
        globalStates.add(keyIndexes to checkpointMessage)
    }

    override suspend fun flushReadyCheckpointMessages() {
        if (maxNumFlushAttempts >= 0 && flushedAtMs.size >= maxNumFlushAttempts) {
            throw IllegalStateException("Max number of flushes reached")
        }
        flushedAtMs.add(timeProvider.currentTimeMillis())
    }

    override suspend fun getLastSuccessfulFlushTimeMs(): Long {
        return mockLastFlushTimeMs
    }

    override suspend fun getNextCheckpointIndexes(): Map<DestinationStream.Descriptor, Long> {
        return mockCheckpointIndexes
    }

    override suspend fun awaitAllCheckpointsFlushed() {
        throw NotImplementedError()
    }
}
