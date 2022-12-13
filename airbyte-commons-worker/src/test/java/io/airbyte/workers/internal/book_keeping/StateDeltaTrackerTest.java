/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.book_keeping;

import io.airbyte.workers.internal.book_keeping.StateDeltaTracker.StateDeltaTrackerException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class StateDeltaTrackerTest {

  private static final int STATE_1_HASH = 1;
  private static final int STATE_2_HASH = 2;
  private static final int STATE_3_HASH = Integer.MAX_VALUE;
  private static final int NEVER_ADDED_STATE_HASH = 20;

  private static final short STREAM_INDEX_1 = (short) 111;
  private static final short STREAM_INDEX_2 = (short) 222;
  private static final short STREAM_INDEX_3 = (short) 333;
  private static final short STREAM_INDEX_4 = Short.MAX_VALUE;

  private static final long STATE_1_STREAM_1_COUNT = 11L;
  private static final long STATE_1_STREAM_2_COUNT = 12L;

  private static final long STATE_2_STREAM_1_COUNT = 21L;
  private static final long STATE_2_STREAM_3_COUNT = 23L;

  private static final long STATE_3_STREAM_3_COUNT = 33L;
  private static final long STATE_3_STREAM_4_COUNT = 34L;

  // enough capacity for above 3 states, which are each 24 bytes (8 byte hash + two 10 byte stream
  // counts
  private static final long INITIAL_DELTA_MEMORY_CAPACITY = 72L;

  private StateDeltaTracker stateDeltaTracker;

  @BeforeEach
  void setup() throws Exception {
    final Map<Short, Long> state1Counts = new HashMap<>();
    state1Counts.put(STREAM_INDEX_1, STATE_1_STREAM_1_COUNT);
    state1Counts.put(STREAM_INDEX_2, STATE_1_STREAM_2_COUNT);

    final Map<Short, Long> state2Counts = new HashMap<>();
    state2Counts.put(STREAM_INDEX_1, STATE_2_STREAM_1_COUNT);
    state2Counts.put(STREAM_INDEX_3, STATE_2_STREAM_3_COUNT);

    final Map<Short, Long> state3Counts = new HashMap<>();
    state3Counts.put(STREAM_INDEX_3, STATE_3_STREAM_3_COUNT);
    state3Counts.put(STREAM_INDEX_4, STATE_3_STREAM_4_COUNT);

    stateDeltaTracker = new StateDeltaTracker(INITIAL_DELTA_MEMORY_CAPACITY);
    stateDeltaTracker.addState(STATE_1_HASH, state1Counts);
    stateDeltaTracker.addState(STATE_2_HASH, state2Counts);
    stateDeltaTracker.addState(STATE_3_HASH, state3Counts);
  }

  @Test
  void testAddState_throwsExceptionWhenCapacityExceeded() {
    Assertions.assertThrows(StateDeltaTrackerException.class, () -> stateDeltaTracker.addState(4, Collections.singletonMap((short) 444, 44L)));
    Assertions.assertTrue(stateDeltaTracker.capacityExceeded);
  }

  @Test
  void testCommitStateHash_throwsExceptionWhenStateHashConflict() throws Exception {
    stateDeltaTracker.commitStateHash(STATE_1_HASH);
    stateDeltaTracker.commitStateHash(STATE_2_HASH);

    Assertions.assertThrows(StateDeltaTrackerException.class, () -> stateDeltaTracker.commitStateHash(STATE_1_HASH));
  }

  @Test
  void testCommitStateHash_throwsExceptionIfCapacityExceededEarlier() {
    stateDeltaTracker.capacityExceeded = true;
    Assertions.assertThrows(StateDeltaTrackerException.class, () -> stateDeltaTracker.commitStateHash(STATE_1_HASH));
  }

  @Test
  void testCommitStateHash_throwsExceptionIfCommitStateHashCalledBeforeAddingState() {
    Assertions.assertThrows(StateDeltaTrackerException.class, () -> stateDeltaTracker.commitStateHash(NEVER_ADDED_STATE_HASH));
  }

  @Test
  void testGetCommittedRecordsByStream() throws Exception {
    // before anything is committed, returned map should be empty and deltas should contain three states
    final Map<Short, Long> expected = new HashMap<>();
    Assertions.assertEquals(expected, stateDeltaTracker.getStreamToCommittedRecords());
    Assertions.assertEquals(3, stateDeltaTracker.stateDeltas.size());

    stateDeltaTracker.commitStateHash(STATE_1_HASH);
    expected.put(STREAM_INDEX_1, STATE_1_STREAM_1_COUNT);
    expected.put(STREAM_INDEX_2, STATE_1_STREAM_2_COUNT);
    Assertions.assertEquals(expected, stateDeltaTracker.getStreamToCommittedRecords());
    Assertions.assertEquals(2, stateDeltaTracker.stateDeltas.size());
    expected.clear();

    stateDeltaTracker.commitStateHash(STATE_2_HASH);
    expected.put(STREAM_INDEX_1, STATE_1_STREAM_1_COUNT + STATE_2_STREAM_1_COUNT);
    expected.put(STREAM_INDEX_2, STATE_1_STREAM_2_COUNT);
    expected.put(STREAM_INDEX_3, STATE_2_STREAM_3_COUNT);
    Assertions.assertEquals(expected, stateDeltaTracker.getStreamToCommittedRecords());
    Assertions.assertEquals(1, stateDeltaTracker.stateDeltas.size());
    expected.clear();

    stateDeltaTracker.commitStateHash(STATE_3_HASH);
    expected.put(STREAM_INDEX_1, STATE_1_STREAM_1_COUNT + STATE_2_STREAM_1_COUNT);
    expected.put(STREAM_INDEX_2, STATE_1_STREAM_2_COUNT);
    expected.put(STREAM_INDEX_3, STATE_2_STREAM_3_COUNT + STATE_3_STREAM_3_COUNT);
    expected.put(STREAM_INDEX_4, STATE_3_STREAM_4_COUNT);
    Assertions.assertEquals(expected, stateDeltaTracker.getStreamToCommittedRecords());

    // since all states are committed, capacity should be freed and the delta queue should be empty
    Assertions.assertEquals(INITIAL_DELTA_MEMORY_CAPACITY, stateDeltaTracker.remainingCapacity);
    Assertions.assertEquals(0, stateDeltaTracker.stateDeltas.size());
  }

}
