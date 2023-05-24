/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;
import org.apache.mina.util.ConcurrentHashSet;

public class AsyncStateManager {

  private static StreamDescriptor SENTINEL_GLOBAL_DESC =
      new StreamDescriptor().withName(UUID.randomUUID().toString());

  boolean preState = true;
  private final ConcurrentMap<Long, AtomicLong> stateIdToCounter = new ConcurrentHashMap<>();
  private final ConcurrentMap<StreamDescriptor, LinkedList<Long>> streamToStateIdQ = new ConcurrentHashMap<>();

  private final ConcurrentMap<Long, AirbyteMessage> stateIdToState = new ConcurrentHashMap<>();
  // empty in the STREAM case.

  // Alias-ing only exists in the non-STREAM case where we have to convert existing state ids to one
  // single global id.
  // This only happens once.
  private final Set<Long> aliasIds = new ConcurrentHashSet<>();
  private long retroactiveGlobalStateId = 0;

  // Always assume STREAM to begin, and convert only if needed. Most state is per stream anyway.
  private AirbyteStateMessage.AirbyteStateType stateType = AirbyteStateMessage.AirbyteStateType.STREAM;

  public void trackState(final AirbyteMessage message) {
    if (preState) {
      // instead of checking for global or legacy, check for the inverse of stream.
      stateType = extractStateType(message);
      if (stateType != AirbyteStateMessage.AirbyteStateType.STREAM) {// alias old stream-level state ids to single global state id
        // upon conversion, all previous tracking data structures need to be cleared as we move
        // into the non-STREAM world for correctness.

        aliasIds.addAll(streamToStateIdQ.values().stream().flatMap(Collection::stream).toList());
        streamToStateIdQ.clear();
        retroactiveGlobalStateId = PkWhatever.getNextId();

        this.streamToStateIdQ.put(SENTINEL_GLOBAL_DESC, new LinkedList<>());
        this.streamToStateIdQ.get(SENTINEL_GLOBAL_DESC).add(retroactiveGlobalStateId);

        final long combinedCounter = stateIdToCounter.values()
            .stream()
            .mapToLong(AtomicLong::get)
            .sum();
        this.stateIdToCounter.clear();
        this.stateIdToCounter.put(retroactiveGlobalStateId, new AtomicLong(combinedCounter));
      }
      preState = false;
    }

    closeState(message);
  }

  public long getStateId(final StreamDescriptor streamDescriptor) {
    final StreamDescriptor resolvedDescriptor = stateType == AirbyteStateMessage.AirbyteStateType.STREAM ? streamDescriptor : SENTINEL_GLOBAL_DESC;

    if (!streamToStateIdQ.containsKey(resolvedDescriptor)) {
      registerNewStreamDescriptor(resolvedDescriptor);
    }
    // no unboxing should happen since we always guarantee the Long exists.
    return streamToStateIdQ.get(streamDescriptor).peekLast();
  }

  // called by the flush workers per message
  public void decrement(final long stateId) {
    stateIdToCounter.get(getStateAfterAlias(stateId)).decrementAndGet();
  }

  // Always try to flush all states with 0 counters.
  public List<AirbyteMessage> flushStates() {
    final List<AirbyteMessage> output = new ArrayList<>();
    // for each stream
    for (final Map.Entry<StreamDescriptor, LinkedList<Long>> entry : streamToStateIdQ.entrySet()) {
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

  private AirbyteStateMessage.AirbyteStateType extractStateType(final AirbyteMessage message) {
    if (message.getState().getType() == null) {
      // Treated the same as GLOBAL.
      return AirbyteStateMessage.AirbyteStateType.LEGACY;
    } else {
      return message.getState().getType();
    }
  }

  private void closeState(final AirbyteMessage message) {
    final StreamDescriptor resolvedDescriptor = extractStream(message).orElse(SENTINEL_GLOBAL_DESC);
    stateIdToState.put(getStateId(resolvedDescriptor), message);
    registerNewStateId(resolvedDescriptor);
  }

  private static Optional<StreamDescriptor> extractStream(final AirbyteMessage message) {
    return Optional.ofNullable(message.getState().getStream()).map(AirbyteStreamState::getStreamDescriptor);
  }

  private long getStateAfterAlias(final long stateId) {
    if (aliasIds.contains(stateId)) {
      return retroactiveGlobalStateId;
    } else {
      return stateId;
    }
  }

  private void registerNewStreamDescriptor(final StreamDescriptor resolvedDescriptor) {
    streamToStateIdQ.put(resolvedDescriptor, new LinkedList<>());
    registerNewStateId(resolvedDescriptor);
  }

  private void registerNewStateId(final StreamDescriptor resolvedDescriptor) {
    final long stateId = PkWhatever.getNextId();
    streamToStateIdQ.get(resolvedDescriptor).add(stateId);
    stateIdToCounter.put(stateId, new AtomicLong());
  }

  private static class PkWhatever {

    private static long pk = 0;

    public static long getNextId() {
      return pk++;
    }

  }

}
