package io.airbyte.cdk.components.cursor

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Instant
import java.util.*
import kotlin.NoSuchElementException

class CursorAirbyteMessageFactory(
    val streamNamespace: String?,
    val streamName: String,
    val emittedAt: Instant,
    val fn: (CursorState) -> JsonNode,
) {

    fun apply(
        seq: Sequence<Pair<Sequence<ObjectNode>, CursorState>>
    ): Sequence<AirbyteMessage> = seq.flatMap { apply(it) }

    fun apply(pair: Pair<Sequence<ObjectNode>, CursorState>): Sequence<AirbyteMessage> =
        Sequence {
            object : Iterator<AirbyteMessage> {
                var n = 0L
                val recordIterator = pair.first.iterator()
                var hasNext = true
                override fun hasNext(): Boolean = hasNext
                override fun next(): AirbyteMessage {
                    if (!hasNext) {
                        throw NoSuchElementException()
                    }
                    if (recordIterator.hasNext()) {
                        n++
                        return AirbyteMessage()
                            .withType(AirbyteMessage.Type.RECORD)
                            .withRecord(AirbyteRecordMessage()
                                .withStream(streamName)
                                .withNamespace(streamNamespace)
                                .withEmittedAt(emittedAt.toEpochMilli())
                                .withData(recordIterator.next()));
                    }
                    hasNext = false
                    return AirbyteMessage()
                        .withType(AirbyteMessage.Type.STATE)
                        .withState(AirbyteStateMessage()
                            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                            .withSourceStats(AirbyteStateStats().withRecordCount(n.toDouble()))
                            .withStream(AirbyteStreamState()
                                .withStreamDescriptor(StreamDescriptor()
                                    .withName(streamName)
                                    .withNamespace(streamNamespace))
                                .withStreamState(fn(pair.second))))
                }
            }
        }
}
