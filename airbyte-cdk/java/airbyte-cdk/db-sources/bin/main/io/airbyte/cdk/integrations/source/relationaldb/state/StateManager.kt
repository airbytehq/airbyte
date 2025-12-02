/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*

private val LOGGER = KotlinLogging.logger {}
/**
 * Defines a manager that manages connector state. Connector state is used to keep track of the data
 * synced by the connector.
 *
 * @param <T> The type of the state maintained by the manager.
 * @param <S> The type of the stream(s) stored within the state maintained by the manager. </S></T>
 */
interface StateManager {
    /**
     * Retrieves the [CdcStateManager] associated with the state manager.
     *
     * @return The [CdcStateManager]
     * @throws UnsupportedOperationException if the state manager does not support tracking change
     * data capture (CDC) state.
     */
    val cdcStateManager: CdcStateManager

    /**
     * Retries the raw state messages associated with the state manager. This is required for
     * database-specific sync modes (e.g. Xmin) that would want to handle and parse their own state
     *
     * @return the list of airbyte state messages
     * @throws UnsupportedOperationException if the state manager does not support retrieving raw
     * state.
     */
    val rawStateMessages: List<AirbyteStateMessage>?

    /**
     * Retrieves the map of stream name/namespace tuple to the current cursor information for that
     * stream.
     *
     * @return The map of stream name/namespace tuple to the current cursor information for that
     * stream as maintained by this state manager.
     */
    val pairToCursorInfoMap: Map<AirbyteStreamNameNamespacePair, CursorInfo>

    /**
     * Generates an [AirbyteStateMessage] that represents the current state contained in the state
     * manager.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] that represents a stream managed by the
     * state manager.
     * @return The [AirbyteStateMessage] that represents the current state contained in the state
     * manager.
     */
    fun toState(pair: Optional<AirbyteStreamNameNamespacePair>): AirbyteStateMessage

    /**
     * Retrieves an [Optional] possibly containing the cursor value tracked in the state associated
     * with the provided stream name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] which identifies a stream.
     * @return An [Optional] possibly containing the cursor value tracked in the state associated
     * with the provided stream name/namespace tuple.
     */
    fun getCursor(pair: AirbyteStreamNameNamespacePair?): Optional<String> {
        return getCursorInfo(pair).map { obj: CursorInfo -> obj.cursor }
    }

    /**
     * Retrieves an [Optional] possibly containing the cursor field name associated with the cursor
     * tracked in the state associated with the provided stream name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] which identifies a stream.
     * @return An [Optional] possibly containing the cursor field name associated with the cursor
     * tracked in the state associated with the provided stream name/namespace tuple.
     */
    fun getCursorField(pair: AirbyteStreamNameNamespacePair?): Optional<String>? {
        return getCursorInfo(pair).map { obj: CursorInfo -> obj.cursorField }
    }

    /**
     * Retrieves an [Optional] possibly containing the original cursor value tracked in the state
     * associated with the provided stream name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] which identifies a stream.
     * @return An [Optional] possibly containing the original cursor value tracked in the state
     * associated with the provided stream name/namespace tuple.
     */
    fun getOriginalCursor(pair: AirbyteStreamNameNamespacePair?): Optional<String>? {
        return getCursorInfo(pair).map { obj: CursorInfo -> obj.originalCursor }
    }

    /**
     * Retrieves an [Optional] possibly containing the original cursor field name associated with
     * the cursor tracked in the state associated with the provided stream name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] which identifies a stream.
     * @return An [Optional] possibly containing the original cursor field name associated with the
     * cursor tracked in the state associated with the provided stream name/namespace tuple.
     */
    fun getOriginalCursorField(pair: AirbyteStreamNameNamespacePair?): Optional<String>? {
        return getCursorInfo(pair).map { obj: CursorInfo -> obj.originalCursorField }
    }

    /**
     * Retrieves the current cursor information stored in the state manager for the steam
     * name/namespace tuple.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] that represents a stream managed by the
     * state manager.
     * @return [Optional] that potentially contains the current cursor information for the given
     * stream name/namespace tuple.
     */
    fun getCursorInfo(pair: AirbyteStreamNameNamespacePair?): Optional<CursorInfo> {
        return Optional.ofNullable(pairToCursorInfoMap[pair])
    }

    /**
     * Emits the current state maintained by the manager as an [AirbyteStateMessage].
     *
     * @param pair The [AirbyteStreamNameNamespacePair] that represents a stream managed by the
     * state manager.
     * @return An [AirbyteStateMessage] that represents the current state maintained by the state
     * manager.
     */
    fun emit(pair: Optional<AirbyteStreamNameNamespacePair>): AirbyteStateMessage? {
        return toState(pair)
    }

    /**
     * Updates the cursor associated with the provided stream name/namespace pair and emits the
     * current state maintained by the state manager.
     *
     * @param pair The [AirbyteStreamNameNamespacePair] that represents a stream managed by the
     * state manager.
     * @param cursor The new value for the cursor associated with the
     * [AirbyteStreamNameNamespacePair] that represents a stream managed by the state manager.
     * @return An [AirbyteStateMessage] that represents the current state maintained by the state
     * manager.
     */
    fun updateAndEmit(pair: AirbyteStreamNameNamespacePair, cursor: String?): AirbyteStateMessage? {
        return updateAndEmit(pair, cursor, 0L)
    }

    fun updateAndEmit(
        pair: AirbyteStreamNameNamespacePair,
        cursor: String?,
        cursorRecordCount: Long
    ): AirbyteStateMessage? {
        val cursorInfo = getCursorInfo(pair)
        Preconditions.checkState(
            cursorInfo.isPresent,
            "Could not find cursor information for stream: $pair"
        )
        cursorInfo.get().setCursor(cursor)
        if (cursorRecordCount > 0L) {
            cursorInfo.get().setCursorRecordCount(cursorRecordCount)
        }
        LOGGER.debug { "Updating cursor value for $pair to $cursor (count $cursorRecordCount)..." }
        return emit(Optional.ofNullable(pair))
    }

    companion object {}
}
