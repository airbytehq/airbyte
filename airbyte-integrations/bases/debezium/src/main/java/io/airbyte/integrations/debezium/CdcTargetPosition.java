/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
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

}
