/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

/**
 * Micronaut factory for the [InputState] singleton.
 *
 * The value may be defined via two Micronaut properties:
 * - `airbyte.connector.state.json` for use by [ConnectorCommandLinePropertySource],
 * - `airbyte.connector.state.resource` for use in unit tests.
 */
@Factory
class InputStateFactory {
    private val log = KotlinLogging.logger {}

    @Singleton
    @Requires(missingProperty = "${CONNECTOR_STATE_PREFIX}.resource")
    fun make(
        @Value("\${${CONNECTOR_STATE_PREFIX}.json}") json: String?,
    ): InputState {
        val list: List<AirbyteStateMessage> =
            ValidatedJsonUtils.parseList(AirbyteStateMessage::class.java, json ?: "[]")
                // Discard states messages with unset type to allow {} as a valid input state.
                .filter { it.type != null }
        if (list.isEmpty()) {
            return EmptyInputState
        }
        for (message in list) {
            validateStateMessage(message)
        }
        val deduped: List<AirbyteStateMessage> =
            list
                .groupBy { msg: AirbyteStateMessage ->
                    if (msg.stream == null) {
                        msg.type.toString()
                    } else {
                        StreamIdentifier.from(msg.stream.streamDescriptor).toString()
                    }
                }
                .mapNotNull { (groupKey, groupValues) ->
                    if (groupValues.size > 1) {
                        log.warn {
                            "Discarded duplicated ${groupValues.size - 1} state message(s) " +
                                "for '$groupKey'."
                        }
                    }
                    groupValues.last()
                }
        val nonGlobalStreams: Map<StreamIdentifier, OpaqueStateValue> =
            streamStates(deduped.mapNotNull { it.stream })
        val globalState: AirbyteGlobalState? =
            deduped.find { it.type == AirbyteStateMessage.AirbyteStateType.GLOBAL }?.global
        if (globalState == null) {
            return StreamInputState(nonGlobalStreams)
        }
        val globalStateValue: OpaqueStateValue =
            ValidatedJsonUtils.parseUnvalidated(
                globalState.sharedState,
                OpaqueStateValue::class.java,
            )
        val globalStreams: Map<StreamIdentifier, OpaqueStateValue> =
            streamStates(globalState.streamStates)
        return GlobalInputState(globalStateValue, globalStreams, nonGlobalStreams)
    }

    private fun streamStates(
        streamStates: List<AirbyteStreamState>?,
    ): Map<StreamIdentifier, OpaqueStateValue> =
        (streamStates ?: listOf()).associate { msg: AirbyteStreamState ->
            val streamID: StreamIdentifier = StreamIdentifier.from(msg.streamDescriptor)
            val jsonValue: JsonNode = msg.streamState ?: Jsons.objectNode()
            streamID to ValidatedJsonUtils.parseUnvalidated(jsonValue, OpaqueStateValue::class.java)
        }

    private fun validateStateMessage(message: AirbyteStateMessage) {
        when (message.type) {
            AirbyteStateMessage.AirbyteStateType.GLOBAL -> {
                if (message.global == null) {
                    throw ConfigErrorException("global state not set in $message.")
                }
            }
            AirbyteStateMessage.AirbyteStateType.STREAM -> {
                if (message.stream == null) {
                    throw ConfigErrorException("stream state not set in $message.")
                }
            }
            else -> {
                throw ConfigErrorException("Unsupported state type ${message.type} in $message.")
            }
        }
    }

    @Singleton
    @Requires(env = [Environment.TEST])
    @Requires(notEnv = [Environment.CLI])
    @Requires(property = "${CONNECTOR_STATE_PREFIX}.resource")
    fun makeFromTestResource(
        @Value("\${${CONNECTOR_STATE_PREFIX}.resource}") resource: String,
    ): InputState = make(ResourceUtils.readResource(resource))
}
