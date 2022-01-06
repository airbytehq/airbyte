/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.annotations.VisibleForTesting;
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
 *
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

  private final ByteBuffer stateHashByteBuffer;
  private final ByteBuffer streamIndexByteBuffer;
  private final ByteBuffer recordCountByteBuffer;
  private final Set<Integer> committedStateHashes;
  private final HashMap<Short, Long> committedRecordsByStream;

  /**
   * Every time a state is added, a new byte[] containing the state hash and per-stream delta will be
   * added to this list. Every time a state is committed, state deltas up to the committed state are
   * removed from the head of the list and aggregated into the committed count map. The source thread
   * adds while the destination thread removes, so those respective methods are synchronized to
   * prevent thread-safety issues.
   */
  @VisibleForTesting
  protected final List<byte[]> stateDeltas;

  @VisibleForTesting
  protected long remainingCapacity;
  @VisibleForTesting
  protected boolean capacityExceeded;

  public StateDeltaTracker(final long memoryLimitBytes) {
    this.stateHashByteBuffer = ByteBuffer.allocate(STATE_HASH_BYTES);
    this.streamIndexByteBuffer = ByteBuffer.allocate(STREAM_INDEX_BYTES);
    this.recordCountByteBuffer = ByteBuffer.allocate(RECORD_COUNT_BYTES);
    this.committedStateHashes = new HashSet<>();
    this.committedRecordsByStream = new HashMap<>();
    this.stateDeltas = new ArrayList<>();
    this.remainingCapacity = memoryLimitBytes;
    this.capacityExceeded = false;
  }

  /**
   * Converts the given state hash and per-stream record count map into a {@code byte[]} and stores
   * it.
   *
   * This method is synchronized to provide thread safety between the source thread calling addState
   * while the destination thread calls commitStateHash.
   *
   * @throws CapacityExceededException thrown when the memory footprint of stateDeltas exceeds
   *         available capacity.
   */
  public synchronized void addState(final int stateHash, final Map<Short, Long> streamIndexToRecordCount) throws CapacityExceededException {
    final int size = STATE_HASH_BYTES + (streamIndexToRecordCount.size() * BYTES_PER_STREAM);

    if (capacityExceeded || remainingCapacity < size) {
      capacityExceeded = true;
      throw new CapacityExceededException("Memory capacity is exceeded for StateDeltaTracker.");
    }

    final byte[] delta = new byte[size];
    int offset = 0;

    stateHashByteBuffer.putInt(stateHash);
    stateHashByteBuffer.flip();
    stateHashByteBuffer.get(delta, offset, STATE_HASH_BYTES);
    stateHashByteBuffer.clear();

    // move offset forward now that the int state hash was inserted
    offset += STATE_HASH_BYTES;

    for (final Map.Entry<Short, Long> entry : streamIndexToRecordCount.entrySet()) {
      streamIndexByteBuffer.putShort(entry.getKey().shortValue());
      streamIndexByteBuffer.flip();
      streamIndexByteBuffer.get(delta, offset, STREAM_INDEX_BYTES);
      streamIndexByteBuffer.clear();

      // move offset forward now that the short stream index was inserted
      offset += STREAM_INDEX_BYTES;

      recordCountByteBuffer.putLong(entry.getValue().longValue());
      recordCountByteBuffer.flip();
      recordCountByteBuffer.get(delta, offset, RECORD_COUNT_BYTES);
      recordCountByteBuffer.clear();

      // move offset forward now that the long record count was inserted
      offset += RECORD_COUNT_BYTES;
    }

    stateDeltas.add(delta);
    remainingCapacity -= delta.length;
  }

  /**
   * Mark the given {@code stateHash} as committed.
   *
   * This method is synchronized to provide thread safety between the source thread calling addState
   * while the destination thread calls commitStateHash.
   *
   * @throws StateHashConflictException thrown when the given {@code stateHash} is already committed
   * @throws CapacityExceededException thrown when committed counts can no longer be reliably computed
   *         due earlier exceeded capacity from addState.
   */
  public synchronized void commitStateHash(final int stateHash) throws StateHashConflictException, CapacityExceededException {
    if (capacityExceeded) {
      throw new CapacityExceededException("Memory capacity exceeded for StateDeltaTracker, so states cannot be reliably committed");
    }
    if (committedStateHashes.contains(stateHash)) {
      throw new StateHashConflictException(String.format("State hash %d was already committed, likely indicating a state hash collision", stateHash));
    }

    this.committedStateHashes.add(stateHash);
    int currStateHash;

    do {
      if (stateDeltas.isEmpty()) {
        // Should never happen as long as addState always called before commitStateHash
        throw new IllegalStateException(String.format("Delta was not stored for state hash %d", stateHash));
      }

      // as deltas are removed and aggregated into committed count map, reclaim capacity
      final byte[] currDelta = stateDeltas.remove(0);
      remainingCapacity += currDelta.length;

      int offset = 0;
      // read stateHash from byte[] and move offset forward
      stateHashByteBuffer.put(currDelta, offset, STATE_HASH_BYTES);
      stateHashByteBuffer.flip();
      currStateHash = stateHashByteBuffer.getInt();
      stateHashByteBuffer.clear();
      offset += STATE_HASH_BYTES;

      final int numStreams = (currDelta.length - STATE_HASH_BYTES) / BYTES_PER_STREAM;
      for (int i = 0; i < numStreams; i++) {
        // read stream index from byte[] and move offset forward
        streamIndexByteBuffer.put(currDelta, offset, STREAM_INDEX_BYTES);
        streamIndexByteBuffer.flip();
        final short streamIndex = streamIndexByteBuffer.getShort();
        streamIndexByteBuffer.clear();
        offset += STREAM_INDEX_BYTES;

        // read record count from byte[] and move offset forward
        recordCountByteBuffer.put(currDelta, offset, RECORD_COUNT_BYTES);
        recordCountByteBuffer.flip();
        final long recordCount = recordCountByteBuffer.getLong();
        recordCountByteBuffer.clear();
        offset += RECORD_COUNT_BYTES;

        // aggregate delta into committed count map
        final long committedRecordCount = committedRecordsByStream.getOrDefault(streamIndex, 0L);
        committedRecordsByStream.put(streamIndex, committedRecordCount + recordCount);
      }
    } while (currStateHash != stateHash); // repeat until each delta up to the committed state is aggregated
  }

  public Map<Short, Long> getCommittedRecordsByStream() {
    return committedRecordsByStream;
  }

  /**
   * Thrown when the StateDeltaTracker capacity has been exceeded, and per-stream record counts cannot
   * be reliably returned.
   */
  public static class CapacityExceededException extends Exception {

    public CapacityExceededException(final String message) {
      super(message);
    }

  }

  /**
   * Thrown when the StateDeltaTracker encounters a state hash that has already been committed, likely
   * indicating a hash conflict.
   */
  public static class StateHashConflictException extends Exception {

    public StateHashConflictException(final String message) {
      super(message);
    }

  }

}
