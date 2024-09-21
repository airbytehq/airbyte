/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.data.AirbyteValue
import io.airbyte.cdk.data.AirbyteValueToJson
import io.airbyte.cdk.data.JsonToAirbyteValue
import io.airbyte.cdk.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.message.CheckpointMessage.Stats
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import jakarta.inject.Singleton

/**
 * Internal representation of destination messages. These are intended to be specialized for
 * usability. Data should be marshalled to these from frontline deserialized objects.
 */
sealed interface DestinationMessage {
    fun asProtocolMessage(): AirbyteMessage
}

/** Records. */
sealed interface DestinationStreamAffinedMessage : DestinationMessage {
    val stream: DestinationStream
}

data class DestinationRecord(
    override val stream: DestinationStream,
    val data: AirbyteValue,
    val emittedAtMs: Long,
    val meta: Meta?,
    val serialized: String,
) : DestinationStreamAffinedMessage {
    data class Meta(val changes: List<Change>?) {
        fun asProtocolObject(): AirbyteRecordMessageMeta =
            AirbyteRecordMessageMeta().also {
                if (changes != null) {
                    it.changes = changes.map { change -> change.asProtocolObject() }
                }
            }
    }

    data class Change(
        val field: String,
        // Using the raw protocol enums here.
        // By definition, we just want to pass these through directly.
        val change: AirbyteRecordMessageMetaChange.Change,
        val reason: AirbyteRecordMessageMetaChange.Reason,
    ) {
        fun asProtocolObject(): AirbyteRecordMessageMetaChange =
            AirbyteRecordMessageMetaChange().withField(field).withChange(change).withReason(reason)
    }

    override fun asProtocolMessage(): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withStream(stream.descriptor.name)
                    .withNamespace(stream.descriptor.namespace)
                    .withEmittedAt(emittedAtMs)
                    .withData(AirbyteValueToJson().convert(data))
                    .also {
                        if (meta != null) {
                            it.meta = meta.asProtocolObject()
                        }
                    }
            )
}

private fun statusToProtocolMessage(
    stream: DestinationStream,
    emittedAtMs: Long,
    status: AirbyteStreamStatus,
): AirbyteMessage =
    AirbyteMessage()
        .withType(AirbyteMessage.Type.TRACE)
        .withTrace(
            AirbyteTraceMessage()
                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                .withEmittedAt(emittedAtMs.toDouble())
                .withStreamStatus(
                    AirbyteStreamStatusTraceMessage()
                        .withStreamDescriptor(stream.descriptor.asProtocolObject())
                        .withStatus(status)
                )
        )

data class DestinationStreamComplete(
    override val stream: DestinationStream,
    val emittedAtMs: Long,
) : DestinationStreamAffinedMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.COMPLETE)
}

data class DestinationStreamIncomplete(
    override val stream: DestinationStream,
    val emittedAtMs: Long,
) : DestinationStreamAffinedMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.INCOMPLETE)
}

/** State. */
sealed interface CheckpointMessage : DestinationMessage {
    data class Stats(val recordCount: Long)
    data class Checkpoint(
        val stream: DestinationStream,
        val state: JsonNode,
    ) {
        fun asProtocolObject(): AirbyteStreamState =
            AirbyteStreamState()
                .withStreamDescriptor(stream.descriptor.asProtocolObject())
                .withStreamState(state)
    }

    val sourceStats: Stats
    val destinationStats: Stats?

    fun withDestinationStats(stats: Stats): CheckpointMessage
}

data class StreamCheckpoint(
    val checkpoint: Checkpoint,
    override val sourceStats: Stats,
    override val destinationStats: Stats? = null
) : CheckpointMessage {
    override fun withDestinationStats(stats: Stats) =
        StreamCheckpoint(checkpoint, sourceStats, stats)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(checkpoint.asProtocolObject())
                .withSourceStats(
                    AirbyteStateStats().withRecordCount(sourceStats.recordCount.toDouble())
                )
                .also {
                    if (destinationStats != null) {
                        it.destinationStats =
                            AirbyteStateStats()
                                .withRecordCount(destinationStats.recordCount.toDouble())
                    }
                }
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}

data class GlobalCheckpoint(
    val state: JsonNode,
    override val sourceStats: Stats,
    override val destinationStats: Stats? = null,
    val checkpoints: List<Checkpoint> = emptyList()
) : CheckpointMessage {
    override fun withDestinationStats(stats: Stats) =
        GlobalCheckpoint(state, sourceStats, stats, checkpoints)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(state)
                        .withStreamStates(checkpoints.map { it.asProtocolObject() })
                )
                .withSourceStats(
                    AirbyteStateStats().withRecordCount(sourceStats.recordCount.toDouble())
                )
                .also {
                    if (destinationStats != null) {
                        it.destinationStats =
                            AirbyteStateStats()
                                .withRecordCount(destinationStats.recordCount.toDouble())
                    }
                }
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}

/** Catchall for anything unimplemented. */
data object Undefined : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage {
        // Arguably we could accept the raw message in the constructor?
        // But that seems weird - when would we ever want to reemit that message?
        throw NotImplementedError(
            "Unrecognized messages cannot be safely converted back to a protocol object."
        )
    }
}

@Singleton
class DestinationMessageFactory(private val catalog: DestinationCatalog) {
    fun fromAirbyteMessage(message: AirbyteMessage, serialized: String): DestinationMessage {
        return when (message.type) {
            AirbyteMessage.Type.RECORD -> {
                val stream =
                    catalog.getStream(
                        namespace = message.record.namespace,
                        name = message.record.stream,
                    )
                DestinationRecord(
                    stream = stream,
                    data = JsonToAirbyteValue().convert(message.record.data, stream.schema),
                    emittedAtMs = message.record.emittedAt,
                    meta =
                        message.record.meta?.let { meta ->
                            DestinationRecord.Meta(
                                meta.changes?.map {
                                    DestinationRecord.Change(
                                        field = it.field,
                                        change = it.change,
                                        reason = it.reason,
                                    )
                                }
                            )
                        },
                    serialized = serialized
                )
            }
            AirbyteMessage.Type.TRACE -> {
                val status = message.trace.streamStatus
                val stream =
                    catalog.getStream(
                        namespace = status.streamDescriptor.namespace,
                        name = status.streamDescriptor.name,
                    )
                if (message.trace.type == AirbyteTraceMessage.Type.STREAM_STATUS) {
                    when (status.status) {
                        AirbyteStreamStatus.COMPLETE ->
                            DestinationStreamComplete(stream, message.trace.emittedAt.toLong())
                        AirbyteStreamStatus.INCOMPLETE ->
                            DestinationStreamIncomplete(stream, message.trace.emittedAt.toLong())
                        else -> Undefined
                    }
                } else {
                    Undefined
                }
            }
            AirbyteMessage.Type.STATE -> {
                when (message.state.type) {
                    AirbyteStateMessage.AirbyteStateType.STREAM ->
                        StreamCheckpoint(
                            checkpoint = fromAirbyteStreamState(message.state.stream),
                            sourceStats =
                                Stats(recordCount = message.state.sourceStats.recordCount.toLong())
                        )
                    AirbyteStateMessage.AirbyteStateType.GLOBAL ->
                        GlobalCheckpoint(
                            sourceStats =
                                Stats(recordCount = message.state.sourceStats.recordCount.toLong()),
                            state = message.state.global.sharedState,
                            checkpoints =
                                message.state.global.streamStates.map { fromAirbyteStreamState(it) }
                        )
                    else -> // TODO: Do we still need to handle LEGACY?
                    Undefined
                }
            }
            else -> Undefined
        }
    }

    private fun fromAirbyteStreamState(streamState: AirbyteStreamState): Checkpoint {
        val descriptor = streamState.streamDescriptor
        return Checkpoint(
            stream = catalog.getStream(namespace = descriptor.namespace, name = descriptor.name),
            state = streamState.streamState
        )
    }
}
