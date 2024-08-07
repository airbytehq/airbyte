/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import java.util.*
import java.util.function.Supplier

/**
 * Global implementation of the [StateManager] interface.
 *
 * This implementation generates a single, global state object for the state tracked by this
 * manager.
 */
class GlobalStateManager(
    airbyteStateMessage: AirbyteStateMessage,
    catalog: ConfiguredAirbyteCatalog
) :
    AbstractStateManager<AirbyteStateMessage, AirbyteStreamState>(
        catalog,
        getStreamsSupplier(airbyteStateMessage),
        StateGeneratorUtils.CURSOR_FUNCTION,
        StateGeneratorUtils.CURSOR_FIELD_FUNCTION,
        StateGeneratorUtils.CURSOR_RECORD_COUNT_FUNCTION,
        StateGeneratorUtils.NAME_NAMESPACE_PAIR_FUNCTION,
        true
    ) {
    /**
     * Legacy [CdcStateManager] used to manage state for connectors that support Change Data Capture
     * (CDC).
     */
    override val cdcStateManager: CdcStateManager

    /**
     * Constructs a new [GlobalStateManager] that is seeded with the provided [AirbyteStateMessage].
     *
     * @param airbyteStateMessage The initial state represented as an [AirbyteStateMessage].
     * @param catalog The [ConfiguredAirbyteCatalog] for the connector associated with this state
     * manager.
     */
    init {
        this.cdcStateManager =
            CdcStateManager(
                extractCdcState(airbyteStateMessage),
                extractStreams(airbyteStateMessage),
                airbyteStateMessage
            )
    }

    override val rawStateMessages: List<AirbyteStateMessage>?
        get() {
            throw UnsupportedOperationException(
                "Raw state retrieval not supported by global state manager."
            )
        }

    override fun toState(pair: Optional<AirbyteStreamNameNamespacePair>): AirbyteStateMessage {
        // Populate global state
        val globalState = AirbyteGlobalState()
        globalState.sharedState = Jsons.jsonNode(cdcStateManager.cdcState)
        // If stream state exists in the global manager, it should be used to reflect the partial
        // states of initial loads.
        if (
            cdcStateManager.rawStateMessage?.global?.streamStates != null &&
                cdcStateManager.rawStateMessage.global?.streamStates?.size != 0
        ) {
            globalState.streamStates = cdcStateManager.rawStateMessage.global.streamStates
        } else {
            globalState.streamStates =
                StateGeneratorUtils.generateStreamStateList(pairToCursorInfoMap)
        }

        // Generate the legacy state for backwards compatibility
        val dbState =
            StateGeneratorUtils.generateDbState(pairToCursorInfoMap)
                .withCdc(true)
                .withCdcState(cdcStateManager.cdcState)

        return AirbyteStateMessage()
            .withType(
                AirbyteStateMessage.AirbyteStateType.GLOBAL
            ) // Temporarily include legacy state for backwards compatibility with the platform
            .withData(Jsons.jsonNode(dbState))
            .withGlobal(globalState)
    }

    /**
     * Extracts the Change Data Capture (CDC) state stored in the initial state provided to this
     * state manager.
     *
     * @param airbyteStateMessage The [AirbyteStateMessage] that contains the initial state provided
     * to the state manager.
     * @return The [CdcState] stored in the state, if any. Note that this will not be `null` but may
     * be empty.
     */
    private fun extractCdcState(airbyteStateMessage: AirbyteStateMessage?): CdcState? {
        if (airbyteStateMessage!!.type == AirbyteStateMessage.AirbyteStateType.GLOBAL) {
            return Jsons.`object`(airbyteStateMessage.global.sharedState, CdcState::class.java)
        } else {
            val legacyState: DbState? =
                Jsons.`object`(airbyteStateMessage.data, DbState::class.java)
            return legacyState?.cdcState
        }
    }

    private fun extractStreams(
        airbyteStateMessage: AirbyteStateMessage?
    ): Set<AirbyteStreamNameNamespacePair> {
        if (airbyteStateMessage!!.type == AirbyteStateMessage.AirbyteStateType.GLOBAL) {
            return airbyteStateMessage.global.streamStates
                .map { streamState: AirbyteStreamState ->
                    val cloned = Jsons.clone(streamState)
                    AirbyteStreamNameNamespacePair(
                        cloned.streamDescriptor.name,
                        cloned.streamDescriptor.namespace
                    )
                }
                .toSet()
        } else {
            val legacyState: DbState? =
                Jsons.`object`(airbyteStateMessage.data, DbState::class.java)
            return if (legacyState != null)
                extractNamespacePairsFromDbStreamState(legacyState.streams)
            else emptySet<AirbyteStreamNameNamespacePair>()
        }
    }

    private fun extractNamespacePairsFromDbStreamState(
        streams: List<DbStreamState>
    ): Set<AirbyteStreamNameNamespacePair> {
        return streams
            .map { stream: DbStreamState ->
                val cloned = Jsons.clone(stream)
                AirbyteStreamNameNamespacePair(cloned.streamName, cloned.streamNamespace)
            }
            .toSet()
    }

    companion object {
        /**
         * Generates the [Supplier] that will be used to extract the streams from the incoming
         * [AirbyteStateMessage].
         *
         * @param airbyteStateMessage The [AirbyteStateMessage] supplied to this state manager with
         * the initial state.
         * @return A [Supplier] that will be used to fetch the streams present in the initial state.
         */
        private fun getStreamsSupplier(
            airbyteStateMessage: AirbyteStateMessage?
        ): Supplier<Collection<AirbyteStreamState>> {
            /*
             * If the incoming message has the state type set to GLOBAL, it is using the new format. Therefore,
             * we can look for streams in the "global" field of the message. Otherwise, the message is still
             * storing state in the legacy "data" field.
             */
            return Supplier {
                if (airbyteStateMessage!!.type == AirbyteStateMessage.AirbyteStateType.GLOBAL) {
                    return@Supplier airbyteStateMessage.global.streamStates
                } else if (airbyteStateMessage.data != null) {
                    return@Supplier Jsons.`object`<DbState>(
                            airbyteStateMessage.data,
                            DbState::class.java
                        )!!
                        .streams
                        .map { s: DbStreamState ->
                            AirbyteStreamState()
                                .withStreamState(Jsons.jsonNode<DbStreamState>(s))
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withNamespace(s.streamNamespace)
                                        .withName(s.streamName)
                                )
                        }
                } else {
                    return@Supplier listOf<AirbyteStreamState>()
                }
            }
        }
    }
}
