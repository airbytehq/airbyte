/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import io.debezium.engine.ChangeEvent;
import java.util.Map;

/**
 * This interface is used to define the target position at the beginning of the sync so that once we
 * reach the desired target, we can shutdown the sync. This is needed because it might happen that
 * while we are syncing the data, new changes are being made in the source database and as a result
 * we might end up syncing forever. In order to tackle that, we need to define a point to end at the
 * beginning of the sync
 */
public interface CdcTargetPosition<T> {

  /**
   * Reads a position value (ex: LSN) from a change event and compares it to target position
   *
   * @param valueAsJson json representation of a change event
   * @return true if event position is equal or greater than target position, or if last snapshot
   *         event
   */
  boolean reachedTargetPosition(final JsonNode valueAsJson);

  /**
   * Reads a position value (lsn) from a change event and compares it to target lsn
   *
   * @param positionFromHeartbeat is the position extracted out of a heartbeat event (if the connector
   *        supports heartbeat)
   * @return true if heartbeat position is equal or greater than target position
   */
  default boolean reachedTargetPosition(final T positionFromHeartbeat) {
    throw new UnsupportedOperationException();
  }

  /**
   * Indicates whether the implementation supports heartbeat position.
   *
   * @return true if heartbeats are supported
   */
  default boolean isHeartbeatSupported() {
    return false;
  }

  /**
   * Returns a position value from a heartbeat event offset.
   *
   * @param sourceOffset source offset params from heartbeat change event
   * @return the heartbeat position in a heartbeat change event or null
   */
  T extractPositionFromHeartbeatOffset(final Map<String, ?> sourceOffset);

  /**
   * This function indicates if the event is part of the snapshot or not.
   *
   * @param event Event from the CDC load
   * @return Returns `true` when the DB event is part of the snapshot load. Otherwise, returns `false`
   */
  default boolean isSnapshotEvent(final ChangeEvent<String, String> event) {
    return false;
  }

  /**
   * This function checks if the event we are processing in the loop is already behind the offset so
   * the process can safety save the state.
   *
   * @param offset DB CDC offset
   * @param event Event from the CDC load
   * @return Returns `true` when the record is behind the offset. Otherwise, it returns `false`
   */
  default boolean isRecordBehindOffset(final Map<String, String> offset, final ChangeEvent<String, String> event) {
    return false;
  }

  /**
   * This function compares two offsets to make sure both are not pointing to the same position. The
   * main purpose is to avoid sending same offset multiple times.
   *
   * @param offsetA Offset to compare
   * @param offsetB Offset to compare
   * @return Returns `true` if both offsets are at the same position. Otherwise, it returns `false`
   */
  default boolean isSameOffset(final Map<String, String> offsetA, final Map<String, String> offsetB) {
    return true;
  }

}
