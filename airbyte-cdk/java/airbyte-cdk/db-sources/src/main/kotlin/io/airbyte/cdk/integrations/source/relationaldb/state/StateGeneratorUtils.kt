/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.commons.json.Jsons
import io.airbyte.configoss.StateType
import io.airbyte.configoss.StateWrapper
import io.airbyte.configoss.helpers.StateMessageHelper
import io.airbyte.protocol.models.v0.*
import java.util.*
import java.util.function.Function
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** Collection of utilities that facilitate the generation of state objects. */
object StateGeneratorUtils {
    private val LOGGER: Logger = LoggerFactory.getLogger(StateGeneratorUtils::class.java)

    /** [Function] that extracts the cursor from the stream state. */
    val CURSOR_FUNCTION: Function<AirbyteStreamState, String> =
        Function { stream: AirbyteStreamState ->
            val dbStreamState = extractState(stream)
            dbStreamState.map { obj: DbStreamState -> obj.cursor }.orElse(null)
        }

    /** [Function] that extracts the cursor field(s) from the stream state. */
    val CURSOR_FIELD_FUNCTION: Function<AirbyteStreamState, List<String>> =
        Function { stream: AirbyteStreamState ->
            val dbStreamState = extractState(stream)
            if (dbStreamState.isPresent) {
                return@Function dbStreamState.get().cursorField
            } else {
                return@Function listOf<String>()
            }
        }

    val CURSOR_RECORD_COUNT_FUNCTION: Function<AirbyteStreamState, Long> =
        Function { stream: AirbyteStreamState ->
            val dbStreamState = extractState(stream)
            dbStreamState.map { obj: DbStreamState -> obj.cursorRecordCount }.orElse(0L)
        }

    /** [Function] that creates an [AirbyteStreamNameNamespacePair] from the stream state. */
    val NAME_NAMESPACE_PAIR_FUNCTION:
        Function<AirbyteStreamState, AirbyteStreamNameNamespacePair?> =
        Function { s: AirbyteStreamState ->
            if (isValidStreamDescriptor(s.streamDescriptor))
                AirbyteStreamNameNamespacePair(
                    s.streamDescriptor.name,
                    s.streamDescriptor.namespace
                )
            else null
        }

    /**
     * Generates the stream state for the given stream and cursor information.
     *
     * @param airbyteStreamNameNamespacePair The stream.
     * @param cursorInfo The current cursor.
     * @return The [AirbyteStreamState] representing the current state of the stream.
     */
    fun generateStreamState(
        airbyteStreamNameNamespacePair: AirbyteStreamNameNamespacePair,
        cursorInfo: CursorInfo
    ): AirbyteStreamState {
        return AirbyteStreamState()
            .withStreamDescriptor(
                StreamDescriptor()
                    .withName(airbyteStreamNameNamespacePair.name)
                    .withNamespace(airbyteStreamNameNamespacePair.namespace)
            )
            .withStreamState(
                Jsons.jsonNode(generateDbStreamState(airbyteStreamNameNamespacePair, cursorInfo))
            )
    }

    /**
     * Generates a list of valid stream states from the provided stream and cursor information. A
     * stream state is considered to be valid if the stream has a valid descriptor (see
     * [.isValidStreamDescriptor] for more details).
     *
     * @param pairToCursorInfoMap The map of stream name/namespace tuple to the current cursor
     * information for that stream
     * @return The list of stream states derived from the state information extracted from the
     * provided map.
     */
    fun generateStreamStateList(
        pairToCursorInfoMap: Map<AirbyteStreamNameNamespacePair, CursorInfo>
    ): List<AirbyteStreamState> {
        return pairToCursorInfoMap.entries
            .stream()
            .sorted(java.util.Map.Entry.comparingByKey())
            .map { e: Map.Entry<AirbyteStreamNameNamespacePair, CursorInfo> ->
                generateStreamState(e.key, e.value)
            }
            .filter { s: AirbyteStreamState -> isValidStreamDescriptor(s.streamDescriptor) }
            .toList()
    }

    /**
     * Generates the legacy global state for backwards compatibility.
     *
     * @param pairToCursorInfoMap The map of stream name/namespace tuple to the current cursor
     * information for that stream
     * @return The legacy [DbState].
     */
    fun generateDbState(
        pairToCursorInfoMap: Map<AirbyteStreamNameNamespacePair, CursorInfo>
    ): DbState {
        return DbState()
            .withCdc(false)
            .withStreams(
                pairToCursorInfoMap.entries
                    .stream()
                    .sorted(
                        java.util.Map.Entry.comparingByKey()
                    ) // sort by stream name then namespace for sanity.
                    .map { e: Map.Entry<AirbyteStreamNameNamespacePair, CursorInfo> ->
                        generateDbStreamState(e.key, e.value)
                    }
                    .toList()
            )
    }

    /**
     * Generates the [DbStreamState] for the given stream and cursor.
     *
     * @param airbyteStreamNameNamespacePair The stream.
     * @param cursorInfo The current cursor.
     * @return The [DbStreamState].
     */
    fun generateDbStreamState(
        airbyteStreamNameNamespacePair: AirbyteStreamNameNamespacePair,
        cursorInfo: CursorInfo
    ): DbStreamState {
        val state =
            DbStreamState()
                .withStreamName(airbyteStreamNameNamespacePair.name)
                .withStreamNamespace(airbyteStreamNameNamespacePair.namespace)
                .withCursorField(
                    if (cursorInfo.cursorField == null) emptyList()
                    else Lists.newArrayList(cursorInfo.cursorField)
                )
                .withCursor(cursorInfo.cursor)
        if (cursorInfo.cursorRecordCount > 0L) {
            state.cursorRecordCount = cursorInfo.cursorRecordCount
        }
        return state
    }

    /**
     * Extracts the actual state from the [AirbyteStreamState] object.
     *
     * @param state The [AirbyteStreamState] that contains the actual stream state as JSON.
     * @return An [Optional] possibly containing the deserialized representation of the stream state
     * or an empty [Optional] if the state is not present or could not be deserialized.
     */
    fun extractState(state: AirbyteStreamState): Optional<DbStreamState> {
        try {
            return Optional.ofNullable(Jsons.`object`(state.streamState, DbStreamState::class.java))
        } catch (e: IllegalArgumentException) {
            LOGGER.error("Unable to extract state.", e)
            return Optional.empty()
        }
    }

    /**
     * Tests whether the provided [StreamDescriptor] is valid. A valid descriptor is defined as one
     * that has a non-`null` name.
     *
     * See
     * https://github.com/airbytehq/airbyte/blob/e63458fabb067978beb5eaa74d2bc130919b419f/docs/understanding-airbyte/airbyte-protocol.md
     * for more details
     *
     * @param streamDescriptor A [StreamDescriptor] to be validated.
     * @return `true` if the provided [StreamDescriptor] is valid or `false` if it is invalid.
     */
    fun isValidStreamDescriptor(streamDescriptor: StreamDescriptor?): Boolean {
        return if (streamDescriptor != null) {
            streamDescriptor.name != null
        } else {
            false
        }
    }

    /**
     * Converts a [AirbyteStateType.LEGACY] state message into a [AirbyteStateType.GLOBAL] message.
     *
     * @param airbyteStateMessage A [AirbyteStateType.LEGACY] state message.
     * @return A [AirbyteStateType.GLOBAL] state message.
     */
    @JvmStatic
    fun convertLegacyStateToGlobalState(
        airbyteStateMessage: AirbyteStateMessage
    ): AirbyteStateMessage {
        val dbState = Jsons.`object`(airbyteStateMessage.data, DbState::class.java)!!
        val globalState =
            AirbyteGlobalState()
                .withSharedState(Jsons.jsonNode(dbState.cdcState))
                .withStreamStates(
                    dbState.streams
                        .stream()
                        .map { s: DbStreamState ->
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withName(s.streamName)
                                        .withNamespace(s.streamNamespace)
                                )
                                .withStreamState(Jsons.jsonNode(s))
                        }
                        .toList()
                )
        return AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
            .withGlobal(globalState)
    }

    /**
     * Converts a [AirbyteStateType.LEGACY] state message into a list of [AirbyteStateType.STREAM]
     * messages.
     *
     * @param airbyteStateMessage A [AirbyteStateType.LEGACY] state message.
     * @return A list [AirbyteStateType.STREAM] state messages.
     */
    fun convertLegacyStateToStreamState(
        airbyteStateMessage: AirbyteStateMessage
    ): List<AirbyteStateMessage> {
        return Jsons.`object`(airbyteStateMessage.data, DbState::class.java)!!
            .streams
            .stream()
            .map { s: DbStreamState ->
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                    .withStream(
                        AirbyteStreamState()
                            .withStreamDescriptor(
                                StreamDescriptor()
                                    .withNamespace(s.streamNamespace)
                                    .withName(s.streamName)
                            )
                            .withStreamState(Jsons.jsonNode(s))
                    )
            }
            .toList()
    }

    fun convertStateMessage(
        state: io.airbyte.protocol.models.AirbyteStateMessage
    ): AirbyteStateMessage {
        return Jsons.`object`(Jsons.jsonNode(state), AirbyteStateMessage::class.java)!!
    }

    /**
     * Deserializes the state represented as JSON into an object representation.
     *
     * @param initialStateJson The state as JSON.
     * @Param supportedStateType the [AirbyteStateType] supported by this connector.
     * @return The deserialized object representation of the state.
     */
    @JvmStatic
    fun deserializeInitialState(
        initialStateJson: JsonNode?,
        supportedStateType: AirbyteStateMessage.AirbyteStateType
    ): List<AirbyteStateMessage> {
        val typedState = StateMessageHelper.getTypedState(initialStateJson)
        return typedState
            .map { state: StateWrapper ->
                when (state.stateType) {
                    StateType.GLOBAL -> java.util.List.of(convertStateMessage(state.global))
                    StateType.STREAM -> state.stateMessages.map { convertStateMessage(it) }
                    else ->
                        java.util.List.of(
                            AirbyteStateMessage()
                                .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                                .withData(state.legacyState)
                        )
                }
            }
            .orElse(generateEmptyInitialState(supportedStateType))
    }

    /**
     * Generates an empty, initial state for use by the connector.
     *
     * @Param supportedStateType the [AirbyteStateType] supported by this connector.
     * @return The empty, initial state.
     */
    private fun generateEmptyInitialState(
        supportedStateType: AirbyteStateMessage.AirbyteStateType
    ): List<AirbyteStateMessage> {
        // For backwards compatibility with existing connectors
        if (supportedStateType == AirbyteStateMessage.AirbyteStateType.LEGACY) {
            return java.util.List.of(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                    .withData(Jsons.jsonNode(DbState()))
            )
        } else if (supportedStateType == AirbyteStateMessage.AirbyteStateType.GLOBAL) {
            val globalState =
                AirbyteGlobalState()
                    .withSharedState(Jsons.jsonNode(CdcState()))
                    .withStreamStates(listOf())
            return java.util.List.of(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(globalState)
            )
        } else {
            return java.util.List.of(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                    .withStream(AirbyteStreamState())
            )
        }
    }
}
