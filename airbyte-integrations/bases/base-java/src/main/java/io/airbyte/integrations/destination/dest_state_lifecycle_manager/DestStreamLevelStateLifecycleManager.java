/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;

/**
 * This {@link DestStateLifecycleManager} handles any state where the state messages are scoped by
 * stream. In these cases, at each state of the process, it tracks the LAST state message for EACH
 * stream.
 */
public class DestStreamLevelStateLifecycleManager implements DestStateLifecycleManager {

  private final Map<StreamDescriptor, AirbyteMessage> streamToLastPendingState;
  private final Map<StreamDescriptor, AirbyteMessage> streamToLastFlushedState;
  private final Map<StreamDescriptor, AirbyteMessage> streamToLastCommittedState;

  public DestStreamLevelStateLifecycleManager() {
    this.streamToLastPendingState = new HashMap<>();
    this.streamToLastFlushedState = new HashMap<>();
    this.streamToLastCommittedState = new HashMap<>();
  }

  @Override
  public void addState(final AirbyteMessage message) {
    Preconditions.checkArgument(message.getState().getStateType() == AirbyteStateType.STREAM);
    streamToLastPendingState.put(message.getState().getStream().getStreamDescriptor(), message);
  }

  @Override
  public void markPendingAsFlushed() {
    if (!streamToLastPendingState.isEmpty()) {
      streamToLastFlushedState.putAll(streamToLastPendingState);
      streamToLastPendingState.clear();
    }
  }

  @Override
  public Queue<AirbyteMessage> listFlushed() {
    return new LinkedList<>(streamToLastFlushedState.values());
  }

  @Override
  public void markFlushedAsCommitted() {
    if (!streamToLastFlushedState.isEmpty()) {
      streamToLastCommittedState.putAll(streamToLastFlushedState);
      streamToLastFlushedState.clear();
    }
  }

  @Override
  public Queue<AirbyteMessage> listCommitted() {
    return new LinkedList<>(streamToLastCommittedState.values());
  }

}
