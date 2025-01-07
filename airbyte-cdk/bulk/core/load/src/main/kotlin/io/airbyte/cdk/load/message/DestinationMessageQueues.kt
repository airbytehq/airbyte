/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

interface Sized {
    val sizeBytes: Long
}

/**
 * Wrapper message for stream events published to the stream specific queues, containing metadata
 * like index and size.
 *
 * In a future where we deserialize only the info necessary for routing, this could include a dumb
 * container for the serialized, and deserialization could be deferred until the spooled records
 * were recovered from disk.
 */
sealed class DestinationStreamEvent : Sized

/** Contains a record to be aggregated and processed. */
data class StreamRecordEvent(
    val index: Long,
    override val sizeBytes: Long,
    val payload: DestinationRecordSerialized
) : DestinationStreamEvent()

/**
 * Indicates the stream is in a terminal (complete or incomplete) state as signalled by upstream.
 */
data class StreamEndEvent(
    val index: Long,
) : DestinationStreamEvent() {
    override val sizeBytes: Long = 0L
}

/**
 * Emitted to trigger evaluation of the conditional flush logic of a stream. The consumer may or may
 * not decide to flush.
 */
data class StreamFlushEvent(
    val tickedAtMs: Long,
) : DestinationStreamEvent() {
    override val sizeBytes: Long = 0L
}

class DestinationStreamEventQueue : ChannelMessageQueue<Reserved<DestinationStreamEvent>>()

/**
 * A supplier of message queues to which ([ReservationManager.reserve]'d) @ [DestinationStreamEvent]
 * messages can be published on a @ [DestinationStream] key. The queues themselves do not manage
 * memory.
 */
@Singleton
@Secondary
class DestinationStreamQueueSupplier(catalog: DestinationCatalog) :
    MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>> {
    private val queues =
        ConcurrentHashMap<DestinationStream.Descriptor, DestinationStreamEventQueue>()

    init {
        catalog.streams.forEach { queues[it.descriptor] = DestinationStreamEventQueue() }
    }

    override fun get(key: DestinationStream.Descriptor): DestinationStreamEventQueue {
        return queues[key]
            ?: throw IllegalArgumentException("Reading from non-existent stream: $key")
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
