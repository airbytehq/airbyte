/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.HashMap;
import java.util.Map;
import java.util.NavigableMap;
import java.util.Optional;
import java.util.TreeMap;

/**
 * A state lifecycle is either state tracking for a single stream (in the per-stream state case) or
 * for the global state (in the global or legacy cases).
 * <p>
 * The lifecycle tracks state messages and their respective message numbers. It is resilient to the
 * fact that batches of records may get flushed out of order (by different workers running in
 * different threads). It does this by allowing each batch to report its min and max message number.
 * It will then mark any states in that range as having all its records flushed. Then it looks at
 * the state with the lowest message number and iterates upwards as long as it has not encountered a
 * non-flushed state. It returns the highest flushed state that it can find for which all the states
 * with lowered message numbers are also flushed. This is the best state message that we can emit.
 * <p>
 * The two public methods on this class are `synchronized` as the internals of this class are NOT
 * thread safe.
 */
public class StateLifecycle {

  private final Map<Long, AirbyteMessage> idToState;
  private final Map<AirbyteMessage, Long> stateToId;
  private final NavigableMap<Long, Boolean> stateToIsFlushed;

  public StateLifecycle() {
    idToState = new HashMap<>();
    stateToId = new HashMap<>();
    stateToIsFlushed = new TreeMap<>();
  }

  /**
   * Adds a state message to be tracked. If the same state message is submitted more than once, the
   * subsequent submissions are ignored.
   *
   * @param message message to track
   * @param messageNum message number
   */
  public synchronized void trackState(final AirbyteMessage message, final long messageNum) {
    if (!stateToId.containsKey(message)) {
      idToState.put(messageNum, message);
      stateToId.put(message, messageNum);
      stateToIsFlushed.put(messageNum, false);
    }
  }

  /**
   * Marks the provided state as completed. It then returns the highest state possible. This
   * calculated as the highest state for which itself and all the previous states have been flushed.
   * <p>
   * For example, if BEFORE this message was called S1: not flushed S2: flushed, S3: not flushed, and
   * then this method is called with S3, it will return an empty optional, because even though S3 is
   * flushed, S1 hasn't, so it's not safe to emit any states.
   * <p>
   * Now let's say after that method call our states now look like this. S1: not flushed S2: flushed,
   * S3: flushed. Now, we call this method with S1 and then this method is called with S1. This method
   * would return S3, because all the states through S3 have now been flushed.
   *
   * @param minMessageNum min number that was emitted by batch
   * @param maxMessageNum max number that was emitted by batch
   * @return highest state for which itself and all previous states have been flushed.
   */
  public synchronized Optional<AirbyteMessage> completeState(final long minMessageNum, final long maxMessageNum) {
    boolean allEncountedStatesFlushed = true;
    long bestMessageId = 0;
    for (final Long stateId : stateToIsFlushed.navigableKeySet()) {

      /*
       * first, we make sure set all the state message in range to flushed.
       *
       * +1 because if the next message was the state, then all good.
       */
      if (stateId >= minMessageNum && stateId <= maxMessageNum) {
        stateToIsFlushed.computeIfPresent(stateId, (a, b) -> true);
      }

      /*
       * keep track of any the states we encountered along the way have NOT been flushed.
       */
      if (allEncountedStatesFlushed && !stateToIsFlushed.get(stateId)) {
        allEncountedStatesFlushed = false;
      }

      /*
       * as long as we have not encountered an unflushed state, greedily track the best state we could
       * emit.
       */
      if (allEncountedStatesFlushed) {
        bestMessageId = stateId;
      }

      /*
       * we must keep going to the max value, after that go until we find an unflushed state. that gets us
       * the best state in the case where batches finished out of ord.
       */
      if (stateId > maxMessageNum && !allEncountedStatesFlushed) {
        break;
      }
    }

    if (bestMessageId > 0) {
      final AirbyteMessage airbyteMessage = idToState.get(bestMessageId);
      removeUpTo(bestMessageId);
      return Optional.of(airbyteMessage);
    } else {
      return Optional.empty();
    }
  }

  private void removeUpTo(final long id) {
    final NavigableMap<Long, Boolean> toRemove = stateToIsFlushed.subMap(0L, true, id, true);
    for (final Long nextId : toRemove.navigableKeySet()) {
      final AirbyteMessage message = idToState.get(nextId);
      stateToId.remove(message);
      idToState.remove(nextId);
    }
    toRemove.clear();
  }

}
