/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * This {@link DestStateLifecycleManager} handles any state where there is a guarantee that any
 * single state message represents the state for the ENTIRE connection. At the time of writing,
 * GLOBAL and LEGACY state types are the state type that match this pattern.
 */
public class DestSingleStateLifecycleManager implements DestStateLifecycleManager {

  private AirbyteMessage lastPendingState;
  private AirbyteMessage lastFlushedState;
  private AirbyteMessage lastCommittedState;

  @Override
  public void addState(final AirbyteMessage message) {
    lastPendingState = message;
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
    return new LinkedList<>(lastFlushedState == null ? Collections.emptyList() : List.of(lastFlushedState));
  }

  @Override
  public void markFlushedAsCommitted() {
    if (lastFlushedState != null) {
      lastCommittedState = lastFlushedState;
      lastFlushedState = null;
    }
  }

  @Override
  public Queue<AirbyteMessage> listCommitted() {
    return new LinkedList<>(lastCommittedState == null ? Collections.emptyList() : List.of(lastCommittedState));
  }

}
