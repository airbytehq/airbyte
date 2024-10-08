/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.MemoryManager
import io.airbyte.cdk.load.state.Reserved
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

interface Sized {
    val sizeBytes: Long
}

/**
 * Wrapper for record messages published to the message queue, containing metadata like index and
 * size.
 *
 * In a future where we deserialize only the info necessary for routing, this could include a dumb
 * container for the serialized, and deserialization could be deferred until the spooled records
 * were recovered from disk.
 */
sealed class DestinationRecordWrapped : Sized

data class StreamRecordWrapped(
    val index: Long,
    override val sizeBytes: Long,
    val record: DestinationRecord
) : DestinationRecordWrapped()

data class StreamCompleteWrapped(
    val index: Long,
) : DestinationRecordWrapped() {
    override val sizeBytes: Long = 0L
}

class DestinationRecordQueue : ChannelMessageQueue<Reserved<DestinationRecordWrapped>>()

/**
 * A supplier of message queues to which ([MemoryManager.reserveBlocking]'d) @
 * [DestinationRecordWrapped] messages can be published on a @ [DestinationStream] key. The queues
 * themselves do not manage memory.
 */
@Singleton
@Secondary
class DestinationRecordQueueSupplier(catalog: DestinationCatalog) :
    MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>> {
    private val queues = ConcurrentHashMap<DestinationStream.Descriptor, DestinationRecordQueue>()

    init {
        catalog.streams.forEach { queues[it.descriptor] = DestinationRecordQueue() }
    }

    override fun get(key: DestinationStream.Descriptor): DestinationRecordQueue {
        return queues[key]
            ?: throw IllegalArgumentException("Reading from non-existent record stream: $key")
    }
}

sealed interface CheckpointMessageWrapped : Sized

data class StreamCheckpointWrapped(
    override val sizeBytes: Long,
    val stream: DestinationStream.Descriptor,
    val index: Long,
    val checkpoint: CheckpointMessage
) : CheckpointMessageWrapped

data class GlobalCheckpointWrapped(
    override val sizeBytes: Long,
    val streamIndexes: List<Pair<DestinationStream.Descriptor, Long>>,
    val checkpoint: CheckpointMessage
) : CheckpointMessageWrapped

/**
 * A single-channel queue for checkpoint messages. This is so updating the checkpoint manager never
 * blocks reading from stdin.
 */
@Singleton
@Secondary
class CheckpointMessageQueue : ChannelMessageQueue<Reserved<CheckpointMessageWrapped>>()
