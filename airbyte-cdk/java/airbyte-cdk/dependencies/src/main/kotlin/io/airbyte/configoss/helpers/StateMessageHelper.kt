/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss.helpers

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.json.Jsons.`object`
import io.airbyte.configoss.State
import io.airbyte.configoss.StateType
import io.airbyte.configoss.StateWrapper
import io.airbyte.protocol.models.AirbyteStateMessage
import java.util.*

object StateMessageHelper {
    /**
     * This a takes a json blob state and tries return either a legacy state in the format of a json
     * object or a state message with the new format which is a list of airbyte state message.
     *
     * @param state
     * - a blob representing the state
     * @return An optional state wrapper, if there is no state an empty optional will be returned
     */
    fun getTypedState(state: JsonNode?): Optional<StateWrapper> {
        if (state == null) {
            return Optional.empty()
        } else {
            val stateMessages: List<AirbyteStateMessage>?
            try {
                stateMessages = `object`(state, AirbyteStateMessageListTypeReference())
            } catch (e: IllegalArgumentException) {
                return Optional.of(getLegacyStateWrapper(state))
            }
            if (stateMessages!!.isEmpty()) {
                return Optional.empty()
            }

            if (stateMessages.size == 1) {
                return if (stateMessages[0].type == null) {
                    Optional.of(getLegacyStateWrapper(state))
                } else {
                    when (stateMessages[0].type) {
                        AirbyteStateMessage.AirbyteStateType.GLOBAL -> {
                            Optional.of(provideGlobalState(stateMessages[0]))
                        }
                        AirbyteStateMessage.AirbyteStateType.STREAM -> {
                            Optional.of(provideStreamState(stateMessages))
                        }
                        AirbyteStateMessage.AirbyteStateType.LEGACY -> {
                            Optional.of(getLegacyStateWrapper(stateMessages[0].data))
                        }
                        else -> {
                            // Should not be reachable.
                            throw IllegalStateException("Unexpected state type")
                        }
                    }
                }
            } else {
                if (
                    stateMessages.all { stateMessage: AirbyteStateMessage ->
                        stateMessage.type == AirbyteStateMessage.AirbyteStateType.STREAM
                    }
                ) {
                    return Optional.of(provideStreamState(stateMessages))
                }
                if (
                    stateMessages.all { stateMessage: AirbyteStateMessage ->
                        stateMessage.type == null
                    }
                ) {
                    return Optional.of(getLegacyStateWrapper(state))
                }

                throw IllegalStateException(
                    "Unexpected state blob, the state contains either multiple global or conflicting state type."
                )
            }
        }
    }

    /**
     * Converts a StateWrapper to a State
     *
     * LegacyStates are directly serialized into the state. GlobalStates and StreamStates are
     * serialized as a list of AirbyteStateMessage in the state attribute.
     *
     * @param stateWrapper the StateWrapper to convert
     * @return the Converted State
     */
    fun getState(stateWrapper: StateWrapper): State {
        return when (stateWrapper.stateType) {
            StateType.LEGACY -> State().withState(stateWrapper.legacyState)
            StateType.STREAM -> State().withState(jsonNode(stateWrapper.stateMessages))
            StateType.GLOBAL -> State().withState(jsonNode(java.util.List.of(stateWrapper.global)))
            else -> throw RuntimeException("Unexpected StateType " + stateWrapper.stateType)
        }
    }

    fun isMigration(currentStateType: StateType, previousState: Optional<StateWrapper>): Boolean {
        return previousState.isPresent &&
            isMigration(currentStateType, previousState.get().stateType)
    }

    fun isMigration(currentStateType: StateType, previousStateType: StateType?): Boolean {
        return previousStateType == StateType.LEGACY && currentStateType != StateType.LEGACY
    }

    private fun provideGlobalState(stateMessages: AirbyteStateMessage): StateWrapper {
        return StateWrapper().withStateType(StateType.GLOBAL).withGlobal(stateMessages)
    }

    /**
     * This is returning a wrapped state, it assumes that the state messages are ordered.
     *
     * @param stateMessages
     * - an ordered list of state message
     * @param useStreamCapableState
     * - a flag that indicates whether to return the new format
     * @return a wrapped state
     */
    private fun provideStreamState(stateMessages: List<AirbyteStateMessage>): StateWrapper {
        return StateWrapper().withStateType(StateType.STREAM).withStateMessages(stateMessages)
    }

    private fun getLegacyStateWrapper(state: JsonNode): StateWrapper {
        return StateWrapper().withStateType(StateType.LEGACY).withLegacyState(state)
    }

    class AirbyteStateMessageListTypeReference : TypeReference<List<AirbyteStateMessage>>()
}
