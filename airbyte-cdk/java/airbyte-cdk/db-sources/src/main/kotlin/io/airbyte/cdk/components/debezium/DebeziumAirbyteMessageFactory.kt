/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import java.time.Instant
import java.util.*

/**
 * [DebeziumAirbyteMessageFactory] maps [DebeziumRecord] and [DebeziumState] to [AirbyteMessage].
 */
class DebeziumAirbyteMessageFactory(
    val stateManager: StateManager,
    val emittedAt: Instant,
    val toAirbyteRecord: (DebeziumRecord) -> AirbyteRecordMessage
) {
    fun apply(
        seq: Sequence<Pair<Sequence<DebeziumRecord>, DebeziumState>>
    ): Sequence<AirbyteMessage> = seq.flatMap { apply(it) }

    fun apply(pair: Pair<Sequence<DebeziumRecord>, DebeziumState>): Sequence<AirbyteMessage> =
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
                        val airbyteRecord = toAirbyteRecord(recordIterator.next())
                        return AirbyteMessage()
                            .withType(AirbyteMessage.Type.RECORD)
                            .withRecord(airbyteRecord.withEmittedAt(emittedAt.toEpochMilli()))
                    }
                    hasNext = false
                    stateManager.cdcStateManager.cdcState = toCdcState(pair.second)
                    val stateMessage =
                        stateManager
                            // Namespace pair is ignored by global state manager, but is needed for
                            // satisfy the API contract.
                            .emit(Optional.empty())
                            .withSourceStats(AirbyteStateStats().withRecordCount(n.toDouble()))
                    return AirbyteMessage()
                        .withType(AirbyteMessage.Type.STATE)
                        .withState(stateMessage)
                }
            }
        }

    fun stateFromManager(): Optional<DebeziumState> =
        Optional.ofNullable(stateManager.cdcStateManager.cdcState?.state)
            .map { cdcState ->
                (cdcState as ObjectNode)
                    .fields()
                    .asSequence()
                    .map { Pair(Jsons.deserialize(it.key), Jsons.deserialize(it.value.asText())) }
                    .toMap()
            }
            .map { DebeziumState(DebeziumState.Offset(it), Optional.empty()) }

    companion object {
        @JvmStatic
        fun toCdcState(debeziumState: DebeziumState): CdcState {
            val json = Jsons.emptyObject() as ObjectNode
            for ((k, v) in debeziumState.offset.debeziumOffset) {
                json.put(Jsons.serialize(k), Jsons.serialize(v))
            }
            return CdcState().withState(json)
        }
    }
}
