/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * This class tracks "deltas" between states in compact {@code byte[]}s with the following schema:
 * <pre>{@code
 *  [<state hash><stream index><record count>...] with the last two elements repeating per stream in the delta.
 * }</pre>
 * <p>
 * This class also maintains a {@code Set} of {@code committedStateHashes} so that it can accumulate both
 * committed and total record counts per stream.
 */
public class StateDeltaTracker {

  private static final int STATE_HASH_BYTES = Integer.BYTES;
  private static final int STREAM_INDEX_BYTES = Short.BYTES;
  private static final int RECORD_COUNT_BYTES = Long.BYTES;
  private static final int BYTES_PER_STREAM = STREAM_INDEX_BYTES + RECORD_COUNT_BYTES;

  private final ByteBuffer stateHashByteBuffer;
  private final ByteBuffer streamIndexByteBuffer;
  private final ByteBuffer recordCountByteBuffer;
  private final Set<Integer> committedStateHashes;
  private final List<byte[]> stateDeltas;

  public StateDeltaTracker() {
    this.stateDeltas = new ArrayList<>();
    this.stateHashByteBuffer = ByteBuffer.allocate(STATE_HASH_BYTES);
    this.streamIndexByteBuffer = ByteBuffer.allocate(STREAM_INDEX_BYTES);
    this.recordCountByteBuffer = ByteBuffer.allocate(RECORD_COUNT_BYTES);
    this.committedStateHashes = new HashSet<>();
  }

  public void addState(final int stateHash, final Map<Short, Long> streamIndexToRecordCount) {
    final byte[] delta = new byte[STATE_HASH_BYTES + (streamIndexToRecordCount.size() * BYTES_PER_STREAM)]; // state hash + room for every stream
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

    this.stateDeltas.add(delta);
  }

  /**
   * Mark the given {@code stateHash} as committed.
   *
   * @throws IllegalStateException thrown when the given {@code stateHash} is already committed
   */
  public void commitStateHash(final int stateHash) {
    if (committedStateHashes.contains(stateHash)) {
      throw new IllegalStateException(String.format("State hash %d was already committed, likely indicating a state hash collision", stateHash));
    }

    this.committedStateHashes.add(stateHash);
  }

  /**
   * Iterate over all deltas to compute a total record count per stream.
   *
   * @param committedOnly Indicates whether or not uncommitted deltas should be excluded from the returned total.
   */
  public Map<Short, Long> getStreamIndexToTotalRecordCount(final boolean committedOnly) {
    final Map<Short, Long> streamIndexToTotalRecordCount = new HashMap<>();

    for (final byte[] delta : this.stateDeltas) {
      int offset = 0;

      // read stateHash from byte[] and move offset forward
      stateHashByteBuffer.put(delta, offset, STATE_HASH_BYTES);
      stateHashByteBuffer.flip();
      final int stateHash = stateHashByteBuffer.getInt();
      stateHashByteBuffer.clear();
      offset += STATE_HASH_BYTES;

      // if only counting committed states and the current state is not committed, skip to next byte[]
      if (committedOnly && !committedStateHashes.contains(stateHash)) {
        continue;
      }

      final int numStreams = (delta.length - STATE_HASH_BYTES) / BYTES_PER_STREAM;

      for (int i = 0; i < numStreams; i++) {
        // read stream index from byte[] and move offset forward
        streamIndexByteBuffer.put(delta, offset, STREAM_INDEX_BYTES);
        streamIndexByteBuffer.flip();
        final short streamIndex = streamIndexByteBuffer.getShort();
        streamIndexByteBuffer.clear();
        offset += STREAM_INDEX_BYTES;

        // read record count from byte[] and move offset forward
        recordCountByteBuffer.put(delta, offset, RECORD_COUNT_BYTES);
        recordCountByteBuffer.flip();
        final long recordCount = recordCountByteBuffer.getLong();
        recordCountByteBuffer.clear();
        offset += RECORD_COUNT_BYTES;

        long totalRecordCount = streamIndexToTotalRecordCount.getOrDefault(streamIndex, 0L);
        totalRecordCount += recordCount;
        streamIndexToTotalRecordCount.put(streamIndex, totalRecordCount);
      }
    }
    return streamIndexToTotalRecordCount;
  }
}
