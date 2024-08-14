/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import jakarta.inject.Singleton

/**
 * Internal representation of destination messages. These are intended to be specialized for
 * usability. Data should be marshalled to these from frontline deserialized objects.
 */
sealed class DestinationMessage

/** Records. */
sealed class DestinationRecordMessage : DestinationMessage() {
    abstract val stream: DestinationStream
}

data class DestinationRecord(
    override val stream: DestinationStream,
    val data: JsonNode? = null,
    val emittedAtMs: Long,
    val serialized: String
) : DestinationRecordMessage()

data class DestinationStreamComplete(
    override val stream: DestinationStream,
    val emittedAtMs: Long
) : DestinationRecordMessage()

/** State. */
sealed class DestinationStateMessage : DestinationMessage() {
    data class Stats(val recordCount: Long)
    data class StreamState(
        val stream: DestinationStream,
        val state: JsonNode,
    )

    abstract val sourceStats: Stats
    abstract val destinationStats: Stats?

    abstract fun withDestinationStats(stats: Stats): DestinationStateMessage
}

data class DestinationStreamState(
    val streamState: StreamState,
    override val sourceStats: Stats,
    override val destinationStats: Stats? = null
) : DestinationStateMessage() {
    override fun withDestinationStats(stats: Stats) =
        DestinationStreamState(streamState, sourceStats, stats)
}

data class DestinationGlobalState(
    val state: JsonNode,
    override val sourceStats: Stats,
    override val destinationStats: Stats? = null,
    val streamStates: List<StreamState> = emptyList()
) : DestinationStateMessage() {
    override fun withDestinationStats(stats: Stats) =
        DestinationGlobalState(state, sourceStats, stats, streamStates)
}

/** Catchall for anything unimplemented. */
data object Undefined : DestinationMessage()

@Singleton
class DestinationMessageFactory(private val catalog: DestinationCatalog) {
    fun fromAirbyteMessage(message: AirbyteMessage, serialized: String): DestinationMessage {
        return when (message.type) {
            AirbyteMessage.Type.RECORD ->
                DestinationRecord(
                    stream =
                        catalog.getStream(
                            namespace = message.record.namespace,
                            name = message.record.stream,
                        ),
                    // TODO: Map to AirbyteType
                    data = message.record.data,
                    emittedAtMs = message.record.emittedAt,
                    serialized = serialized
                )
            AirbyteMessage.Type.TRACE -> {
                val status = message.trace.streamStatus
                val stream =
                    catalog.getStream(
                        namespace = status.streamDescriptor.namespace,
                        name = status.streamDescriptor.name,
                    )
                if (
                    message.trace.type == AirbyteTraceMessage.Type.STREAM_STATUS &&
                        status.status == AirbyteStreamStatus.COMPLETE
                ) {
                    DestinationStreamComplete(stream, message.trace.emittedAt.toLong())
                } else {
                    Undefined
                }
            }
            AirbyteMessage.Type.STATE -> {
                when (message.state.type) {
                    AirbyteStateMessage.AirbyteStateType.STREAM ->
                        DestinationStreamState(
                            streamState = fromAirbyteStreamState(message.state.stream),
                            sourceStats =
                                DestinationStateMessage.Stats(
                                    recordCount = message.state.sourceStats.recordCount.toLong()
                                )
                        )
                    AirbyteStateMessage.AirbyteStateType.GLOBAL ->
                        DestinationGlobalState(
                            sourceStats =
                                DestinationStateMessage.Stats(
                                    recordCount = message.state.sourceStats.recordCount.toLong()
                                ),
                            state = message.state.global.sharedState,
                            streamStates =
                                message.state.global.streamStates.map { fromAirbyteStreamState(it) }
                        )
                    else -> // TODO: Do we still need to handle LEGACY?
                    Undefined
                }
            }
            else -> Undefined
        }
    }

    private fun fromAirbyteStreamState(
        streamState: AirbyteStreamState
    ): DestinationStateMessage.StreamState {
        val descriptor = streamState.streamDescriptor
        return DestinationStateMessage.StreamState(
            stream = catalog.getStream(namespace = descriptor.namespace, name = descriptor.name),
            state = streamState.streamState
        )
    }
}
