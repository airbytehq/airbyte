/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Queue;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * This {@link DestStateLifecycleManager} handles any state where the state messages are scoped by
 * stream. In these cases, at each state of the process, it tracks the LAST state message for EACH
 * stream (no duplicates!).
 *
 * Guaranteed to output state messages in order relative to other messages of the SAME state. Does
 * NOT guarantee that state messages of different streams will be output in the order in which they
 * were received.
 */
public class DestStreamStateLifecycleManager implements DestStateLifecycleManager {

  private final Map<StreamDescriptor, AirbyteMessage> streamToLastPendingState;
  private final Map<StreamDescriptor, AirbyteMessage> streamToLastFlushedState;
  private final Map<StreamDescriptor, AirbyteMessage> streamToLastCommittedState;

  public DestStreamStateLifecycleManager() {
    streamToLastPendingState = new HashMap<>();
    streamToLastFlushedState = new HashMap<>();
    streamToLastCommittedState = new HashMap<>();
  }

  @Override
  public void addState(final AirbyteMessage message) {
    Preconditions.checkArgument(message.getState().getStateType() == AirbyteStateType.STREAM);
    streamToLastPendingState.put(message.getState().getStream().getStreamDescriptor(), message);
  }

  private static Queue<AirbyteMessage> listStatesInOrder(final Map<StreamDescriptor, AirbyteMessage> streamToState) {
    return streamToState
        .entrySet()
        .stream()
        // typically, we support by namespace and then stream name, so we retain that pattern here.
        .sorted(Comparator
            .comparing(
                (Function<Entry<StreamDescriptor, AirbyteMessage>, String>) entry -> entry.getKey().getNamespace(),
                Comparator.nullsFirst(Comparator.naturalOrder())) // namespace is allowed to be null
            .thenComparing(entry -> entry.getKey().getName()))
        .map(Entry::getValue)
        .collect(Collectors.toCollection(LinkedList::new));
  }

  @VisibleForTesting
  Queue<AirbyteMessage> listPending() {
    return listStatesInOrder(streamToLastPendingState);
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
    return listStatesInOrder(streamToLastFlushedState);
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
    return listStatesInOrder(streamToLastCommittedState);
  }

}
