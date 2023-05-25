/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import com.google.common.base.Preconditions;
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
import lombok.extern.slf4j.Slf4j;
import org.apache.mina.util.ConcurrentHashSet;

/**
 * Responsible for managing state within the Destination. The general approach is a ref counter
 * approach - each state message is associated with a record count. This count represents the number
 * of preceding records. For a state to be emitted, all preceding records have to be written to the
 * destination i.e. the counter is 0.
 * <p>
 * A per-stream state queue is maintained internally, with each state within the queue having a
 * counter. This means we *ALLOW* records succeeding an unemitted state to be written. This
 * decouples record writing from state management at the cost of potentially repeating work if an
 * upstream state is never written.
 * <p>
 * One important detail here is the difference between how PER-STREAM & NON-PER-STREAM is handled.
 * The PER-STREAM case is simple, and is as described above. The NON-PER-STREAM case is slightly
 * tricky. Because we don't know the stream type to begin with, we always assume PER_STREAM until
 * the first state message arrives. If this state message is a GLOBAL state, we alias all existing
 * state ids to a single global state id via a set of alias ids. From then onwards, we use one id -
 * {@link #SENTINEL_GLOBAL_DESC} regardless of stream. Read
 * {@link #convertToGlobalIfNeeded(AirbyteMessage)} for more detail.
 */
@Slf4j
public class GlobalAsyncStateManager {

  private static final StreamDescriptor SENTINEL_GLOBAL_DESC = new StreamDescriptor().withName(UUID.randomUUID().toString());

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

  /**
   * Main method to process state messages.
   * <p>
   * The first incoming state message tells us the type of state we are dealing with. We then convert
   * internal data structures if needed.
   * <p>
   * Because state messages are a watermark, all preceding records need to be flushed before the state
   * message can be processed.
   */
  public void trackState(final AirbyteMessage message) {
    if (preState) {
      convertToGlobalIfNeeded(message);
      preState = false;
    }
    // stateType should not change after a conversion.
    Preconditions.checkArgument(stateType == extractStateType(message));

    closeState(message);
  }

  /**
   * Identical to {@link #getStateId(StreamDescriptor)} except this increments the associated counter
   * by 1. Intended to be called whenever a record is ingested.
   *
   * @param streamDescriptor - stream to get stateId for.
   * @return state id
   */
  public long getStateIdAndIncrementCounter(final StreamDescriptor streamDescriptor) {
    return getStateIdAndIncrement(streamDescriptor, 1);
  }

  /**
   * Each decrement represent one written record for a state. A zero counter means there are no more
   * inflight records associated with a state and the state can be flushed.
   *
   * @param stateId reference to a state.
   * @param count to decrement.
   */
  public void decrement(final long stateId, final long count) {
    log.trace("decrementing state id: {}, count: {}", stateId, count);
    stateIdToCounter.get(getStateAfterAlias(stateId)).addAndGet(-count);
  }

  /**
   * Returns state messages with no more inflight records i.e. counter = 0 across all streams.
   * Intended to be called by {@link io.airbyte.integrations.destination_async.FlushWorkers} after a
   * worker has finished flushing its record batch.
   * <p>
   * The return list of states should be emitted back to the platform.
   *
   * @return list of state messages with no more inflight records.
   */
  public List<AirbyteMessage> flushStates() {
    final List<AirbyteMessage> output = new ArrayList<>();
    for (final Map.Entry<StreamDescriptor, LinkedList<Long>> entry : streamToStateIdQ.entrySet()) {
      // remove all states with 0 counters.
      final LinkedList<Long> stateIdQueue = entry.getValue();
      while (true) {
        final Long oldestState = stateIdQueue.peek();
        final boolean emptyQ = oldestState == null;
        final boolean noCorrespondingStateMsg = stateIdToState.get(oldestState) == null;
        if (emptyQ || noCorrespondingStateMsg) {
          break;
        }

        final boolean noPrevRecs = !stateIdToCounter.containsKey(oldestState);
        final boolean allRecsEmitted = stateIdToCounter.get(oldestState).get() == 0;
        if (noPrevRecs || allRecsEmitted) {
          stateIdQueue.poll(); // poll to remove. no need to read as the earlier peek is still valid.
          output.add(stateIdToState.get(oldestState));
        } else {
          break;
        }
      }
    }
    return output;
  }

  private Long getStateIdAndIncrement(final StreamDescriptor streamDescriptor, final long increment) {
    final StreamDescriptor resolvedDescriptor = stateType == AirbyteStateMessage.AirbyteStateType.STREAM ? streamDescriptor : SENTINEL_GLOBAL_DESC;
    if (!streamToStateIdQ.containsKey(resolvedDescriptor)) {
      registerNewStreamDescriptor(resolvedDescriptor);
    }
    final Long stateId = streamToStateIdQ.get(resolvedDescriptor).peekLast();
    final var update = stateIdToCounter.get(stateId).addAndGet(increment);
    log.trace("State id: {}, count: {}", stateId, update);
    return stateId;
  }

  /**
   * Return the internal id of a state message. This is the id that should be used to reference a
   * state when interacting with all methods in this class.
   *
   * @param streamDescriptor - stream to get stateId for.
   * @return state id
   */
  private long getStateId(final StreamDescriptor streamDescriptor) {
    return getStateIdAndIncrement(streamDescriptor, 0);
  }

  /**
   * Because the
   */
  private void convertToGlobalIfNeeded(final AirbyteMessage message) {
    // instead of checking for global or legacy, check for the inverse of stream.
    stateType = extractStateType(message);
    if (stateType != AirbyteStateMessage.AirbyteStateType.STREAM) {// alias old stream-level state ids to single global state id
      // upon conversion, all previous tracking data structures need to be cleared as we move
      // into the non-STREAM world for correctness.

      aliasIds.addAll(streamToStateIdQ.values().stream().flatMap(Collection::stream).toList());
      streamToStateIdQ.clear();
      retroactiveGlobalStateId = StateIdProvider.getNextId();

      streamToStateIdQ.put(SENTINEL_GLOBAL_DESC, new LinkedList<>());
      streamToStateIdQ.get(SENTINEL_GLOBAL_DESC).add(retroactiveGlobalStateId);

      final long combinedCounter = stateIdToCounter.values()
          .stream()
          .mapToLong(AtomicLong::get)
          .sum();
      stateIdToCounter.clear();
      stateIdToCounter.put(retroactiveGlobalStateId, new AtomicLong(combinedCounter));
    }
  }

  private AirbyteStateMessage.AirbyteStateType extractStateType(final AirbyteMessage message) {
    if (message.getState().getType() == null) {
      // Treated the same as GLOBAL.
      return AirbyteStateMessage.AirbyteStateType.LEGACY;
    } else {
      return message.getState().getType();
    }
  }

  /**
   * When a state message is received, 'close' the previous state to associate the existing state id
   * to the newly arrived state message. We also increment the state id in preparation for the next
   * state message.
   */
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
    final long stateId = StateIdProvider.getNextId();
    streamToStateIdQ.get(resolvedDescriptor).add(stateId);
    stateIdToCounter.put(stateId, new AtomicLong(0));
  }

  /**
   * Simplify internal tracking by providing a global always increasing counter for state ids.
   */
  private static class StateIdProvider {

    private static long pk = 0;

    public static long getNextId() {
      return pk++;
    }

  }

}
