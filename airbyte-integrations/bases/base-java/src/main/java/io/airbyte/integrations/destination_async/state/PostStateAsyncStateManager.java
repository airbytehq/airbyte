/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Queue;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;

// todo (cgardens) - hook it up to the memory manager.
public class PostStateAsyncStateManager {

  private final Map<StreamDescriptor, Queue<Long>> streamToStateId;
  private final Map<StreamDescriptor, Long> streamToOpenState;
  private final Map<Long, AirbyteMessage> stateIdToState;
  private final Map<Long, AtomicLong> stateIdToCounter;

  private final Set<Long> aliasIds;
  private final long aliasedId;

  private long lastStateId;

  private final AirbyteStateType stateType;

  public PostStateAsyncStateManager(final AirbyteStateType stateType,
                                    final ConcurrentMap<StreamDescriptor, Long> streamToStateId,
                                    final ConcurrentMap<Long, AtomicLong> stateIdToCounter,
                                    final long lastStateId,
                                    final AirbyteMessage initialState) {
    // same regardless of state type.
    this.stateType = stateType;
    this.lastStateId = lastStateId;
    this.streamToStateId = new ConcurrentHashMap<>();
    this.streamToOpenState = new ConcurrentHashMap<>();
    this.stateIdToState = new ConcurrentHashMap<>();
    this.stateIdToCounter = new ConcurrentHashMap<>();

    if (stateType == AirbyteStateType.STREAM) {
      // not relevant in stream.
      aliasedId = 0L;
      aliasIds = new HashSet<>();

      // for each stream load it into maps.
      for (final Entry<StreamDescriptor, Long> e : streamToStateId.entrySet()) {
        final StreamDescriptor streamDescriptor = e.getKey();
        final long stateId = e.getValue();

        // copied from registerNewStreamDescriptor
        this.streamToStateId.put(streamDescriptor, new LinkedList<>());
        // copied from registerNewStateId
        this.streamToStateId.get(streamDescriptor).add(stateId);
        this.streamToOpenState.put(streamDescriptor, stateId);
        this.stateIdToCounter.put(stateId, new AtomicLong());
      }

      // set up initial state.
      closeState(initialState);
    } else {
      // alias old stream-level state ids to single global state id
      aliasIds = new HashSet<>(streamToStateId.values());
      aliasedId = this.lastStateId++;

      // copied from registerNewStreamDescriptor
      this.streamToStateId.put(null, new LinkedList<>());
      // copied from registerNewStateId
      this.streamToStateId.get(null).add(aliasedId);
      this.streamToOpenState.put(null, aliasedId);
      final long combinedCounter = stateIdToCounter.values()
          .stream()
          .mapToLong(AtomicLong::get)
          .sum();
      this.stateIdToCounter.put(aliasedId, new AtomicLong(combinedCounter));

      // set up initial state.
      closeState(initialState);
    }

    // streamToStateId = new ConcurrentHashMap<>();
    // streamToOpenState = new ConcurrentHashMap<>();
    // stateIdToState = new ConcurrentHashMap<>();
    // stateIdToCounter = new ConcurrentHashMap<>();
  }

  public long getStateId(final StreamDescriptor streamDescriptor) {
    final StreamDescriptor resolvedDescriptor = stateType == AirbyteStateType.STREAM ? streamDescriptor : null;

    if (!streamToStateId.containsKey(resolvedDescriptor)) {
      registerNewStreamDescriptor(resolvedDescriptor);
    }

    return streamToOpenState.get(streamDescriptor);
  }

  public void decrement(final long stateId) {
    stateIdToCounter.get(getStateAfterAlias(stateId)).decrementAndGet();
  }

  private long getStateAfterAlias(final long stateId) {
    if (aliasIds.contains(stateId)) {
      return aliasedId;
    } else {
      return stateId;
    }
  }

  public void trackState(final AirbyteMessage message) {
    closeState(message);
  }

  public List<AirbyteMessage> flushStates() {
    final List<AirbyteMessage> output = new ArrayList<>();
    // for each stream
    for (final Map.Entry<StreamDescriptor, Queue<Long>> entry : streamToStateId.entrySet()) {
      // walk up the states until we find one that has a non zero counter.
      while (true) {
        final Long peek = entry.getValue().peek();
        if (stateIdToCounter.get(peek).get() == 0) {
          entry.getValue().poll();
          output.add(stateIdToState.get(peek));
        } else {
          break;
        }
      }
    }
    return output;
  }

  private void registerNewStreamDescriptor(final StreamDescriptor resolvedDescriptor) {
    streamToStateId.put(resolvedDescriptor, new LinkedList<>());
    registerNewStateId(resolvedDescriptor);
  }

  private void registerNewStateId(final StreamDescriptor resolvedDescriptor) {
    final long stateId = lastStateId++;
    streamToStateId.get(resolvedDescriptor).add(stateId);
    streamToOpenState.put(resolvedDescriptor, stateId);
    stateIdToCounter.put(stateId, new AtomicLong());
    // stateIdToState intentionally left blank. we don'tk now it yet.
  }

  private void closeState(final AirbyteMessage message) {
    final StreamDescriptor resolvedDescriptor = extractStream(message).orElse(null);
    stateIdToState.put(getStateId(resolvedDescriptor), message);
    registerNewStateId(resolvedDescriptor);
  }

  private static Optional<StreamDescriptor> extractStream(final AirbyteMessage message) {
    return Optional.ofNullable(message.getState().getStream()).map(AirbyteStreamState::getStreamDescriptor);
  }

}
