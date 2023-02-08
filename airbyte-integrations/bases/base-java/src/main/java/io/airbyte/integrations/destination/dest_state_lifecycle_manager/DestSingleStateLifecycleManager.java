/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * This {@link DestStateLifecycleManager} handles any state where there is a guarantee that any
 * single state message represents the state for the ENTIRE connection. At the time of writing,
 * GLOBAL and LEGACY state types are the state type that match this pattern.
 *
 * <p>
 * Does NOT store duplicates. Because each state message represents the entire state for the
 * connection, it only stores (and emits) the LAST state it received at each phase.
 * </p>
 */
public class DestSingleStateLifecycleManager implements DestStateLifecycleManager {

  private AirbyteMessage lastPendingState;
  private AirbyteMessage lastFlushedState;
  private AirbyteMessage lastCommittedState;

  @Override
  public void addState(final AirbyteMessage message) {
    lastPendingState = message;
  }

  @VisibleForTesting
  Queue<AirbyteMessage> listPending() {
    return stateMessageToQueue(lastPendingState);
  }

  @Override
  public void markPendingAsFlushed() {
    if (lastPendingState != null) {
      lastFlushedState = lastPendingState;
      lastPendingState = null;
    }
  }

  @Override
  public Queue<AirbyteMessage> listFlushed() {
    return stateMessageToQueue(lastFlushedState);
  }

  @Override
  public void markFlushedAsCommitted() {
    if (lastFlushedState != null) {
      lastCommittedState = lastFlushedState;
      lastFlushedState = null;
    }
  }

  @Override
  public void clearCommitted() {
    lastCommittedState = null;
  }

  @Override
  public void markPendingAsCommitted() {
    if (lastPendingState != null) {
      lastCommittedState = lastPendingState;
      lastPendingState = null;
    }
  }

  @Override
  public Queue<AirbyteMessage> listCommitted() {
    return stateMessageToQueue(lastCommittedState);
  }

  private static Queue<AirbyteMessage> stateMessageToQueue(final AirbyteMessage stateMessage) {
    return new LinkedList<>(stateMessage == null ? Collections.emptyList() : List.of(stateMessage));
  }

  @Override
  public boolean supportsPerStreamFlush() {
    return false;
  }

}
