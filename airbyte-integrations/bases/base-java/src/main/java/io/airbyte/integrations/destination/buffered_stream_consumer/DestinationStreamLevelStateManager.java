/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;

/**
 * This {@link DestinationStateManager} handles any state where the state messages are scoped by
 * stream. In these cases, at each state of the process, it tracks the LAST state message for EACH
 * stream.
 */
public class DestinationStreamLevelStateManager implements DestinationStateManager {

  private final Map<StreamDescriptor, AirbyteMessage> streamToLastPendingState;
  private final Map<StreamDescriptor, AirbyteMessage> streamToLastFlushedState;
  private final Map<StreamDescriptor, AirbyteMessage> streamToLastCommittedState;

  public DestinationStreamLevelStateManager() {
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
  public Queue<AirbyteMessage> listAllPendingState() {
    return new LinkedList<>(streamToLastPendingState.values());
  }

  @Override
  public void markAllReceivedMessagesAsFlushedToTmpDestination() {
    if (!streamToLastPendingState.isEmpty()) {
      streamToLastFlushedState.putAll(streamToLastPendingState);
      streamToLastPendingState.clear();
    }
  }

  @Override
  public Queue<AirbyteMessage> listAllFlushedButNotCommittedState() {
    return new LinkedList<>(streamToLastFlushedState.values());
  }

  @Override
  public void markAllFlushedMessageAsCommitted() {
    if (!streamToLastFlushedState.isEmpty()) {
      streamToLastCommittedState.putAll(streamToLastFlushedState);
      streamToLastFlushedState.clear();
    }
  }

  @Override
  public Queue<AirbyteMessage> listAllCommittedState() {
    return new LinkedList<>(streamToLastCommittedState.values());
  }

}
