/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}
/** Factory class that creates [StateManager] instances based on the provided state. */
object StateManagerFactory {

    /**
     * Creates a [StateManager] based on the provided state object and catalog. This method will
     * handle the conversion of the provided state to match the requested state manager based on the
     * provided [AirbyteStateType].
     *
     * @param supportedStateType The type of state supported by the connector.
     * @param initialState The deserialized initial state that will be provided to the selected
     * [StateManager].
     * @param catalog The [ConfiguredAirbyteCatalog] for the connector that will utilize the state
     * manager.
     * @return A newly created [StateManager] implementation based on the provided state.
     */
    @JvmStatic
    fun createStateManager(
        supportedStateType: AirbyteStateMessage.AirbyteStateType?,
        initialState: List<AirbyteStateMessage>?,
        catalog: ConfiguredAirbyteCatalog
    ): StateManager {
        if (initialState != null && !initialState.isEmpty()) {
            val airbyteStateMessage = initialState[0]
            when (supportedStateType) {
                AirbyteStateMessage.AirbyteStateType.LEGACY -> {
                    LOGGER.info {
                        "Legacy state manager selected to manage state object with type ${airbyteStateMessage.type}."
                    }
                    @Suppress("deprecation")
                    val retVal: StateManager =
                        LegacyStateManager(
                            Jsons.`object`(airbyteStateMessage.data, DbState::class.java)!!,
                            catalog
                        )
                    return retVal
                }
                AirbyteStateMessage.AirbyteStateType.GLOBAL -> {
                    LOGGER.info {
                        "Global state manager selected to manage state object with type ${airbyteStateMessage.type}."
                    }
                    return GlobalStateManager(generateGlobalState(airbyteStateMessage), catalog)
                }
                AirbyteStateMessage.AirbyteStateType.STREAM -> {
                    LOGGER.info {
                        "Stream state manager selected to manage state object with type ${airbyteStateMessage.type}."
                    }
                    return StreamStateManager(generateStreamState(initialState), catalog)
                }
                else -> {
                    LOGGER.info {
                        "Stream state manager selected to manage state object with type ${airbyteStateMessage.type}."
                    }
                    return StreamStateManager(generateStreamState(initialState), catalog)
                }
            }
        } else {
            throw IllegalArgumentException(
                "Failed to create state manager due to empty state list."
            )
        }
    }

    /**
     * Handles the conversion between a different state type and the global state. This method
     * handles the following transitions:
     *
     * * Stream -> Global (not supported, results in [IllegalArgumentException]
     * * Legacy -> Global (supported)
     * * Global -> Global (supported/no conversion required)
     *
     * @param airbyteStateMessage The current state that is to be converted to global state.
     * @return The converted state message.
     * @throws IllegalArgumentException if unable to convert between the given state type and
     * global.
     */
    private fun generateGlobalState(airbyteStateMessage: AirbyteStateMessage): AirbyteStateMessage {
        var globalStateMessage = airbyteStateMessage

        when (airbyteStateMessage.type) {
            AirbyteStateMessage.AirbyteStateType.STREAM ->
                throw ConfigErrorException(
                    "You've changed replication modes - please reset the streams in this connector"
                )
            AirbyteStateMessage.AirbyteStateType.LEGACY -> {
                globalStateMessage =
                    StateGeneratorUtils.convertLegacyStateToGlobalState(airbyteStateMessage)
                LOGGER.info { "Legacy state converted to global state." }
            }
            AirbyteStateMessage.AirbyteStateType.GLOBAL -> {}
            else -> {}
        }
        return globalStateMessage
    }

    /**
     * Handles the conversion between a different state type and the stream state. This method
     * handles the following transitions:
     *
     * * Global -> Stream (not supported, results in [IllegalArgumentException]
     * * Legacy -> Stream (supported)
     * * Stream -> Stream (supported/no conversion required)
     *
     * @param states The list of current states.
     * @return The converted state messages.
     * @throws IllegalArgumentException if unable to convert between the given state type and
     * stream.
     */
    private fun generateStreamState(states: List<AirbyteStateMessage>): List<AirbyteStateMessage> {
        val airbyteStateMessage = states[0]
        val streamStates: MutableList<AirbyteStateMessage> = ArrayList()
        when (airbyteStateMessage.type) {
            AirbyteStateMessage.AirbyteStateType.GLOBAL ->
                throw ConfigErrorException(
                    "You've changed replication modes - please reset the streams in this connector"
                )
            AirbyteStateMessage.AirbyteStateType.LEGACY ->
                streamStates.addAll(
                    StateGeneratorUtils.convertLegacyStateToStreamState(airbyteStateMessage)
                )
            AirbyteStateMessage.AirbyteStateType.STREAM -> streamStates.addAll(states)
            else -> streamStates.addAll(states)
        }
        return streamStates
    }
}
