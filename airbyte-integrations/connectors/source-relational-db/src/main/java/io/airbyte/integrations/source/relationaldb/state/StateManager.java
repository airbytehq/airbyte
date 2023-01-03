/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import com.google.common.base.Preconditions;
import io.airbyte.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Defines a manager that manages connector state. Connector state is used to keep track of the data
 * synced by the connector.
 *
 * @param <T> The type of the state maintained by the manager.
 * @param <S> The type of the stream(s) stored within the state maintained by the manager.
 */
public interface StateManager<T, S> {

  Logger LOGGER = LoggerFactory.getLogger(StateManager.class);

  /**
   * Retrieves the {@link CdcStateManager} associated with the state manager.
   *
   * @return The {@link CdcStateManager}
   * @throws UnsupportedOperationException if the state manager does not support tracking change data
   *         capture (CDC) state.
   */
  CdcStateManager getCdcStateManager();

  /**
   * Retrieves the map of stream name/namespace tuple to the current cursor information for that
   * stream.
   *
   * @return The map of stream name/namespace tuple to the current cursor information for that stream
   *         as maintained by this state manager.
   */
  Map<AirbyteStreamNameNamespacePair, CursorInfo> getPairToCursorInfoMap();

  /**
   * Generates an {@link AirbyteStateMessage} that represents the current state contained in the state
   * manager.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} that represents a stream managed by the
   *        state manager.
   * @return The {@link AirbyteStateMessage} that represents the current state contained in the state
   *         manager.
   */
  AirbyteStateMessage toState(final Optional<AirbyteStreamNameNamespacePair> pair);

  /**
   * Retrieves an {@link Optional} possibly containing the cursor value tracked in the state
   * associated with the provided stream name/namespace tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} which identifies a stream.
   * @return An {@link Optional} possibly containing the cursor value tracked in the state associated
   *         with the provided stream name/namespace tuple.
   */
  default Optional<String> getCursor(final AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getCursor);
  }

  /**
   * Retrieves an {@link Optional} possibly containing the cursor field name associated with the
   * cursor tracked in the state associated with the provided stream name/namespace tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} which identifies a stream.
   * @return An {@link Optional} possibly containing the cursor field name associated with the cursor
   *         tracked in the state associated with the provided stream name/namespace tuple.
   */
  default Optional<String> getCursorField(final AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getCursorField);
  }

  /**
   * Retrieves an {@link Optional} possibly containing the original cursor value tracked in the state
   * associated with the provided stream name/namespace tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} which identifies a stream.
   * @return An {@link Optional} possibly containing the original cursor value tracked in the state
   *         associated with the provided stream name/namespace tuple.
   */
  default Optional<String> getOriginalCursor(final AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getOriginalCursor);
  }

  /**
   * Retrieves an {@link Optional} possibly containing the original cursor field name associated with
   * the cursor tracked in the state associated with the provided stream name/namespace tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} which identifies a stream.
   * @return An {@link Optional} possibly containing the original cursor field name associated with
   *         the cursor tracked in the state associated with the provided stream name/namespace tuple.
   */
  default Optional<String> getOriginalCursorField(final AirbyteStreamNameNamespacePair pair) {
    return getCursorInfo(pair).map(CursorInfo::getOriginalCursorField);
  }

  /**
   * Retrieves the current cursor information stored in the state manager for the steam name/namespace
   * tuple.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} that represents a stream managed by the
   *        state manager.
   * @return {@link Optional} that potentially contains the current cursor information for the given
   *         stream name/namespace tuple.
   */
  default Optional<CursorInfo> getCursorInfo(final AirbyteStreamNameNamespacePair pair) {
    return Optional.ofNullable(getPairToCursorInfoMap().get(pair));
  }

  /**
   * Emits the current state maintained by the manager as an {@link AirbyteStateMessage}.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} that represents a stream managed by the
   *        state manager.
   * @return An {@link AirbyteStateMessage} that represents the current state maintained by the state
   *         manager.
   */
  default AirbyteStateMessage emit(final Optional<AirbyteStreamNameNamespacePair> pair) {
    return toState(pair);
  }

  /**
   * Updates the cursor associated with the provided stream name/namespace pair and emits the current
   * state maintained by the state manager.
   *
   * @param pair The {@link AirbyteStreamNameNamespacePair} that represents a stream managed by the
   *        state manager.
   * @param cursor The new value for the cursor associated with the
   *        {@link AirbyteStreamNameNamespacePair} that represents a stream managed by the state
   *        manager.
   * @return An {@link AirbyteStateMessage} that represents the current state maintained by the state
   *         manager.
   */
  default AirbyteStateMessage updateAndEmit(final AirbyteStreamNameNamespacePair pair, final String cursor) {
    return updateAndEmit(pair, cursor, 0L);
  }

  default AirbyteStateMessage updateAndEmit(final AirbyteStreamNameNamespacePair pair, final String cursor, final long cursorRecordCount) {
    final Optional<CursorInfo> cursorInfo = getCursorInfo(pair);
    Preconditions.checkState(cursorInfo.isPresent(), "Could not find cursor information for stream: " + pair);
    cursorInfo.get().setCursor(cursor);
    if (cursorRecordCount > 0L) {
      cursorInfo.get().setCursorRecordCount(cursorRecordCount);
    }
    LOGGER.debug("Updating cursor value for {} to {} (count {})...", pair, cursor, cursorRecordCount);
    return emit(Optional.ofNullable(pair));
  }

}
