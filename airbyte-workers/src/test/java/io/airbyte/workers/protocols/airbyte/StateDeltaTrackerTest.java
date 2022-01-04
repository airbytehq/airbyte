package io.airbyte.workers.protocols.airbyte;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class StateDeltaTrackerTest {

  private static final int STATE_1_HASH = 1;
  private static final int STATE_2_HASH = 2;
  private static final int STATE_3_HASH = Integer.MAX_VALUE;

  private static final short STREAM_INDEX_1 = (short) 111;
  private static final short STREAM_INDEX_2 = (short) 222;
  private static final short STREAM_INDEX_3 = Short.MAX_VALUE;

  private StateDeltaTracker stateDeltaTracker;

  @BeforeEach
  public void setup() {
    stateDeltaTracker = new StateDeltaTracker();
  }

  @Test
  public void testAddStateAndGetStreamIndexToTotalRecordCount() {
    final Map<Short, Long> streamIndexToRecordCount = new HashMap<>();
    final long state1Stream1Count = 10L;
    final long state1Stream2Count = Long.MAX_VALUE;
    streamIndexToRecordCount.put(STREAM_INDEX_1, state1Stream1Count);
    streamIndexToRecordCount.put(STREAM_INDEX_2, state1Stream2Count);

    stateDeltaTracker.addState(STATE_1_HASH, streamIndexToRecordCount);
    streamIndexToRecordCount.clear();

    final long state2Stream1Count = 90L;
    final long state2Stream3Count = 85L;
    streamIndexToRecordCount.put(STREAM_INDEX_1, state2Stream1Count);
    streamIndexToRecordCount.put(STREAM_INDEX_3, state2Stream3Count);

    stateDeltaTracker.addState(STATE_2_HASH, streamIndexToRecordCount);
    streamIndexToRecordCount.clear();

    final long state3Stream3Count = 150L;
    streamIndexToRecordCount.put(STREAM_INDEX_3, state3Stream3Count);
    stateDeltaTracker.addState(STATE_3_HASH, streamIndexToRecordCount);

    final Map<Short, Long> expectedStreamIndexToRecordCount = new HashMap<>();
    expectedStreamIndexToRecordCount.put(STREAM_INDEX_1, state1Stream1Count + state2Stream1Count);
    expectedStreamIndexToRecordCount.put(STREAM_INDEX_2, state1Stream2Count);
    expectedStreamIndexToRecordCount.put(STREAM_INDEX_3, state2Stream3Count + state3Stream3Count);

    // total count by stream should include everything
    Assertions.assertEquals(expectedStreamIndexToRecordCount, stateDeltaTracker.getStreamIndexToTotalRecordCount(false));
  }

  @Test
  public void testCommitStateHash() {
    final Map<Short, Long> streamIndexToRecordCount = new HashMap<>();
    final long state1Stream1Count = 10L;
    final long state1Stream2Count = Long.MAX_VALUE;
    streamIndexToRecordCount.put(STREAM_INDEX_1, state1Stream1Count);
    streamIndexToRecordCount.put(STREAM_INDEX_2, state1Stream2Count);

    stateDeltaTracker.addState(STATE_1_HASH, streamIndexToRecordCount);
    streamIndexToRecordCount.clear();

    final long state2Stream1Count = 90L;
    final long state2Stream3Count = 85L;
    streamIndexToRecordCount.put(STREAM_INDEX_1, state2Stream1Count);
    streamIndexToRecordCount.put(STREAM_INDEX_3, state2Stream3Count);

    stateDeltaTracker.addState(STATE_2_HASH, streamIndexToRecordCount);
    streamIndexToRecordCount.clear();

    final long state3Stream3Count = 150L;
    streamIndexToRecordCount.put(STREAM_INDEX_3, state3Stream3Count);
    stateDeltaTracker.addState(STATE_3_HASH, streamIndexToRecordCount);

    // committed count by stream should be empty, as nothing has been committed yet
    Assertions.assertEquals(Collections.emptyMap(), stateDeltaTracker.getStreamIndexToTotalRecordCount(true));

    stateDeltaTracker.commitStateHash(STATE_1_HASH);
    stateDeltaTracker.commitStateHash(STATE_2_HASH);

    final Map<Short, Long> expectedStreamIndexToRecordCount = new HashMap<>();
    expectedStreamIndexToRecordCount.put(STREAM_INDEX_1, state1Stream1Count + state2Stream1Count);
    expectedStreamIndexToRecordCount.put(STREAM_INDEX_2, state1Stream2Count);
    // after committing state 1 and 2, committed count by stream should leave out state3Stream3Count because it was the only count not committed
    expectedStreamIndexToRecordCount.put(STREAM_INDEX_3, state2Stream3Count);

    Assertions.assertEquals(expectedStreamIndexToRecordCount, stateDeltaTracker.getStreamIndexToTotalRecordCount(true));
  }
}
