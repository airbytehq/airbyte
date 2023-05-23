/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

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
public class StreamContract {

  private final NavigableMap<Long, Boolean> maxNumToFlushed;

  public StreamContract() {
    maxNumToFlushed = new TreeMap<>();
  }

  public synchronized void claim(final long maxMessageNum) {
    maxNumToFlushed.put(maxMessageNum, false);
  }

  public synchronized void fulfill(final long maxMessageNum) {
    maxNumToFlushed.computeIfPresent(maxMessageNum, (a, b) -> true);
    // clean up as we go.
    pruneFromBottomToMaxFulfilled();
  }

  private void pruneFromBottomToMaxFulfilled() {
    getFulfilledMax().ifPresent(max -> maxNumToFlushed.subMap(0L, true, max, false).clear());
  }

  public Optional<Long> getClaimedMax() {
    return maxNumToFlushed.isEmpty() ? Optional.empty() : Optional.ofNullable(maxNumToFlushed.lastKey());
  }

  /**
   * From 0 to max fulfilled
   *
   * @return
   */
  public Optional<Long> getFulfilledMax() {
    Long max = null;
    for (final Long nextId : maxNumToFlushed.navigableKeySet()) {
      if (!maxNumToFlushed.get(nextId)) {
        break;
      }
      max = nextId;
    }
    return Optional.ofNullable(max);
  }

}
