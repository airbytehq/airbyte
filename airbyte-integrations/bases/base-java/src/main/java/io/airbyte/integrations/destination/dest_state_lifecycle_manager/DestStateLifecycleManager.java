/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Queue;

/**
 * This class manages the lifecycle of state message. It tracks state messages that are in 3 states:
 * <ol>
 * <li>pending - associated records have been accepted by the connector but has NOT been pushed to
 * the destination</li>
 * <li>flushed - associated records have been flushed to tmp storage in the destination but have NOT
 * been committed</li>
 * <li>committed - associated records have been committed</li>
 * </ol>
 */
public interface DestStateLifecycleManager {

  /**
   * Accepts a state into the manager. The state starts in a pending state.
   *
   * @param message - airbyte message of type state
   */
  void addState(AirbyteMessage message);

  /**
   * Moves any tracked state messages that are currently pending to flushed.
   */
  void markPendingAsFlushed();

  /**
   * List all tracked state messages that are flushed.
   *
   * @return list of state messages
   */
  Queue<AirbyteMessage> listFlushed();

  /**
   * Moves any tracked state messages that are currently flushed to committed.
   */
  void markFlushedAsCommitted();

  /**
   * List all tracked state messages that are committed.
   *
   * @return list of state messages
   */
  Queue<AirbyteMessage> listCommitted();

}
