/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.*
import java.util.function.Supplier
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Per-stream implementation of the [StateManager] interface.
 *
 * This implementation generates a state object for each stream detected in catalog/map of known
 * streams to cursor information stored in this manager.
 */
open class StreamStateManager
/**
 * Constructs a new [StreamStateManager] that is seeded with the provided [AirbyteStateMessage].
 *
 * @param airbyteStateMessages The initial state represented as a list of [AirbyteStateMessage]s.
 * @param catalog The [ConfiguredAirbyteCatalog] for the connector associated with this state
 * manager.
 */
(
    private val rawAirbyteStateMessages: List<AirbyteStateMessage>,
    catalog: ConfiguredAirbyteCatalog
) :
    AbstractStateManager<AirbyteStateMessage, AirbyteStreamState>(
        catalog,
        Supplier { rawAirbyteStateMessages.map { it.stream }.toList() },
        StateGeneratorUtils.CURSOR_FUNCTION,
        StateGeneratorUtils.CURSOR_FIELD_FUNCTION,
        StateGeneratorUtils.CURSOR_RECORD_COUNT_FUNCTION,
        StateGeneratorUtils.NAME_NAMESPACE_PAIR_FUNCTION
    ) {
    override val cdcStateManager: CdcStateManager
        get() {
            throw UnsupportedOperationException(
                "CDC state management not supported by stream state manager."
            )
        }

    override val rawStateMessages: List<AirbyteStateMessage?>?
        get() = rawAirbyteStateMessages

    override fun toState(pair: Optional<AirbyteStreamNameNamespacePair>): AirbyteStateMessage {
        if (pair.isPresent) {
            val pairToCursorInfoMap = pairToCursorInfoMap
            val cursorInfo = Optional.ofNullable(pairToCursorInfoMap[pair.get()])

            if (cursorInfo.isPresent) {
                LOGGER.debug("Generating state message for {}...", pair)
                return AirbyteStateMessage()
                    .withType(
                        AirbyteStateMessage.AirbyteStateType.STREAM
                    ) // Temporarily include legacy state for backwards compatibility with the
                    // platform
                    .withData(
                        Jsons.jsonNode(StateGeneratorUtils.generateDbState(pairToCursorInfoMap))
                    )
                    .withStream(
                        StateGeneratorUtils.generateStreamState(pair.get(), cursorInfo.get())
                    )
            } else {
                LOGGER.warn(
                    "Cursor information could not be located in state for stream {}.  Returning a new, empty state message...",
                    pair
                )
                return AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                    .withStream(AirbyteStreamState())
            }
        } else {
            LOGGER.warn("Stream not provided.  Returning a new, empty state message...")
            return AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(AirbyteStreamState())
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(StreamStateManager::class.java)
    }
}
