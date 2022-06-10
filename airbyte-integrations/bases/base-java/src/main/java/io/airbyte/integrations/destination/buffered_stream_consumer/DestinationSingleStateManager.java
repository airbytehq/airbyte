/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * This {@link DestinationStateManager} handles any state where there is a guarantee that any single
 * state message represents the state for the ENTIRE connection. At the time of writing, GLOBAL and
 * LEGACY state types are the state type that match this pattern.
 */
public class DestinationSingleStateManager implements DestinationStateManager {

  private AirbyteMessage pendingState;
  private AirbyteMessage lastFlushedState;
  private AirbyteMessage committedState;

  @Override
  public void addState(final AirbyteMessage message) {
    pendingState = message;
  }

  @Override
  public Queue<AirbyteMessage> listAllPendingState() {
    return new LinkedList<>(List.of(pendingState));
  }

  @Override
  public void markAllReceivedMessagesAsFlushedToTmpDestination() {
    if (pendingState != null) {
      lastFlushedState = pendingState;
      pendingState = null;
    }
  }

  @Override
  public Queue<AirbyteMessage> listAllFlushedButNotCommittedState() {
    return new LinkedList<>(List.of(lastFlushedState));
  }

  @Override
  public void markAllFlushedMessageAsCommitted() {
    if (lastFlushedState != null) {
      committedState = lastFlushedState;
      lastFlushedState = null;
    }
  }

  @Override
  public Queue<AirbyteMessage> listAllCommittedState() {
    return new LinkedList<>(List.of(committedState));
  }

}
