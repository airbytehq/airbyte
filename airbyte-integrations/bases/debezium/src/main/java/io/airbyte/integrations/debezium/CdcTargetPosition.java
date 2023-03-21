/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * This interface is used to define the target position at the beginning of the sync so that once we
 * reach the desired target, we can shutdown the sync. This is needed because it might happen that
 * while we are syncing the data, new changes are being made in the source database and as a result
 * we might end up syncing forever. In order to tackle that, we need to define a point to end at the
 * beginning of the sync
 */
public interface CdcTargetPosition {

  /**
   * Reads a position value (lsn) from a change event and compares it to target lsn
   *
   * @param valueAsJson json representation of a change event
   * @return true if event lsn is equal or greater than targer lsn, or if last snapshot event
   */
  boolean reachedTargetPosition(JsonNode valueAsJson);

  /**
   * Checks if a specified lsn has reached the target lsn.
   *
   * @param lsn an lsn value
   * @return true if lsn is equal or greater than target lsn
   */
  default boolean reachedTargetPosition(final Long lsn) {
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

}
