/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.book_keeping;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import com.google.common.annotations.VisibleForTesting;
import datadog.trace.api.Trace;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import lombok.extern.slf4j.Slf4j;

/**
 * This class tracks "deltas" between states in compact {@code byte[]}s with the following schema:
 *
 * <pre>
 *  [(state hash),(stream index),(record count)...] with the last two elements repeating per stream in the delta.
 * </pre>
 * <p>
 * This class also maintains a {@code Set} of {@code committedStateHashes} so that it can accumulate
 * both committed and total record counts per stream.
 * <p>
 * The StateDeltaTracker is initialized with a memory limit. If this memory limit is exceeded, new
 * states deltas will not be added and per-stream record counts will not be able to be computed.
 * This is to prevent OutOfMemoryErrors from crashing the sync.
 */
@Slf4j
public class StateDeltaTracker {

  private static final int STATE_HASH_BYTES = Integer.BYTES;
  private static final int STREAM_INDEX_BYTES = Short.BYTES;
  private static final int RECORD_COUNT_BYTES = Long.BYTES;
  private static final int BYTES_PER_STREAM = STREAM_INDEX_BYTES + RECORD_COUNT_BYTES;

  private final Set<Integer> committedStateHashes;
  private final Map<Short, Long> streamToCommittedRecords;

  /**
   * Every time a state is added, a new byte[] containing the state hash and per-stream delta will be
   * added to this list. Every time a state is committed, state deltas up to the committed state are
   * removed from the head of the list and aggregated into the committed count map. The source thread
   * adds while the destination thread removes, so synchronization is necessary to provide
   * thread-safety.
   */
  @VisibleForTesting
  protected final List<byte[]> stateDeltas;

  @VisibleForTesting
  protected long remainingCapacity;
  @VisibleForTesting
  protected boolean capacityExceeded;

  public StateDeltaTracker(final long memoryLimitBytes) {
    this.committedStateHashes = new HashSet<>();
    this.streamToCommittedRecords = new HashMap<>();
    this.stateDeltas = new ArrayList<>();
    this.remainingCapacity = memoryLimitBytes;
    this.capacityExceeded = false;
  }

  /**
   * Converts the given state hash and per-stream record count map into a {@code byte[]} and stores
   * it.
   * <p>
   * This method leverages a synchronized block to provide thread safety between the source thread
   * calling addState while the destination thread calls commitStateHash.
   *
   * @throws StateDeltaTrackerException thrown when the memory footprint of stateDeltas exceeds
   *         available capacity.
   */
  @Trace(operationName = WORKER_OPERATION_NAME)
  public void addState(final int stateHash, final Map<Short, Long> streamIndexToRecordCount) throws StateDeltaTrackerException {
    synchronized (this) {
      final int size = STATE_HASH_BYTES + (streamIndexToRecordCount.size() * BYTES_PER_STREAM);

      if (capacityExceeded || remainingCapacity < size) {
        capacityExceeded = true;
        throw new StateDeltaTrackerException("Memory capacity is exceeded for StateDeltaTracker.");
      }

      final ByteBuffer delta = ByteBuffer.allocate(size);

      delta.putInt(stateHash);

      for (final Map.Entry<Short, Long> entry : streamIndexToRecordCount.entrySet()) {
        delta.putShort(entry.getKey());
        delta.putLong(entry.getValue());
      }

      stateDeltas.add(delta.array());
      remainingCapacity -= delta.array().length;
    }
  }

  /**
   * Mark the given {@code stateHash} as committed.
   * <p>
   * This method leverages a synchronized block to provide thread safety between the source thread
   * calling addState while the destination thread calls commitStateHash.
   *
   * @throws StateDeltaTrackerException thrown when committed counts can no longer be reliably
   *         computed.
   */
  @Trace(operationName = WORKER_OPERATION_NAME)
  public void commitStateHash(final int stateHash) throws StateDeltaTrackerException {
    synchronized (this) {
      if (capacityExceeded) {
        throw new StateDeltaTrackerException("Memory capacity exceeded for StateDeltaTracker, so states cannot be reliably committed");
      }
      if (committedStateHashes.contains(stateHash)) {
        throw new StateDeltaTrackerException(
            String.format("State hash %d was already committed, likely indicating a state hash collision", stateHash));
      }

      committedStateHashes.add(stateHash);
      int currStateHash;
      do {
        if (stateDeltas.isEmpty()) {
          throw new StateDeltaTrackerException(String.format("Delta was not stored for state hash %d", stateHash));
        }
        // as deltas are removed and aggregated into committed count map, reclaim capacity
        final ByteBuffer currDelta = ByteBuffer.wrap(stateDeltas.remove(0));
        remainingCapacity += currDelta.capacity();

        currStateHash = currDelta.getInt();

        final int numStreams = (currDelta.capacity() - STATE_HASH_BYTES) / BYTES_PER_STREAM;
        for (int i = 0; i < numStreams; i++) {
          final short streamIndex = currDelta.getShort();
          final long recordCount = currDelta.getLong();

          // aggregate delta into committed count map
          final long committedRecordCount = streamToCommittedRecords.getOrDefault(streamIndex, 0L);
          streamToCommittedRecords.put(streamIndex, committedRecordCount + recordCount);
        }
      } while (currStateHash != stateHash); // repeat until each delta up to the committed state is aggregated
    }
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  public Map<Short, Long> getStreamToCommittedRecords() {
    return streamToCommittedRecords;
  }

  /**
   * Thrown when the StateDeltaTracker encounters an issue that prevents it from reliably computing
   * committed record deltas.
   */
  public static class StateDeltaTrackerException extends Exception {

    public StateDeltaTrackerException(final String message) {
      super(message);
    }

  }

}
