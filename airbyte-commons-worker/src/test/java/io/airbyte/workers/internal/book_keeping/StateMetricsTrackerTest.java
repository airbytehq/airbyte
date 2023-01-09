/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.book_keeping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.workers.internal.book_keeping.StateMetricsTracker.StateMetricsTrackerNoStateMatchException;
import io.airbyte.workers.internal.book_keeping.StateMetricsTracker.StateMetricsTrackerOomException;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class StateMetricsTrackerTest {

  private StateMetricsTracker stateMetricsTracker;
  private static final String STREAM_1 = "stream1";
  private static final String STREAM_2 = "stream2";
  private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String SECOND_ZERO = "2022-01-01 12:00:00";
  private static final String SECOND_ONE = "2022-01-01 12:00:01";
  private static final String SECOND_TWO = "2022-01-01 12:00:02";
  private static final String SECOND_FIVE = "2022-01-01 12:00:05";
  private static final String SECOND_SIX = "2022-01-01 12:00:06";

  @BeforeEach
  void setup() {
    this.stateMetricsTracker = new StateMetricsTracker(873813L);
  }

  @Test
  void testCalculateMean() throws Exception {
    // Mean for 3 state messages is 5, 4th state message is 9, new mean should be 6
    assertEquals(6L, stateMetricsTracker.calculateMean(5L, 4L, 9L));

    // Mean for 5 state messages is 10, 4th state message is 12, new mean is 10.33 rounded down to 10
    assertEquals(10L, stateMetricsTracker.calculateMean(10L, 6L, 12L));
  }

  @Test
  void testStreamMaxandMeanSecondsBetweenStateMessageEmittedandCommitted()
      throws StateMetricsTrackerOomException, StateMetricsTrackerNoStateMatchException {
    final AirbyteStateMessage s1s1 = AirbyteMessageUtils.createStreamStateMessage(STREAM_1, 1);
    final AirbyteStateMessage s1s2 = AirbyteMessageUtils.createStreamStateMessage(STREAM_1, 2);
    final AirbyteStateMessage s1s3 = AirbyteMessageUtils.createStreamStateMessage(STREAM_1, 3);
    final AirbyteStateMessage s2s1 = AirbyteMessageUtils.createStreamStateMessage(STREAM_2, 1);
    final AirbyteStateMessage s2s2 = AirbyteMessageUtils.createStreamStateMessage(STREAM_2, 2);

    stateMetricsTracker.addState(s1s1, 0, LocalDateTime.parse(SECOND_ZERO, FORMATTER)); // stream 1 state
    stateMetricsTracker.addState(s1s2, 1, LocalDateTime.parse(SECOND_ONE, FORMATTER)); // stream 1 state
    stateMetricsTracker.addState(s2s1, 0, LocalDateTime.parse(SECOND_TWO, FORMATTER)); // stream 2 state
    stateMetricsTracker.addState(s1s3, 2, LocalDateTime.parse("2022-01-01 12:00:03", FORMATTER)); // stream 1 state

    // Committed up to 2nd state message in stream 1 - time to commit is 5 seconds (second 00 to second
    // 05)
    stateMetricsTracker.incrementTotalDestinationEmittedStateMessages();
    stateMetricsTracker.updateStates(s1s2, 1, LocalDateTime.parse(SECOND_FIVE, FORMATTER));

    // Committed final state message for stream 1 - time to commit is 7 seconds (second 03 to second 10)
    stateMetricsTracker.incrementTotalDestinationEmittedStateMessages();
    stateMetricsTracker.updateStates(s1s3, 2, LocalDateTime.parse("2022-01-01 12:00:10", FORMATTER));

    stateMetricsTracker.addState(s2s2, 2, LocalDateTime.parse("2022-01-01 12:00:11", FORMATTER));

    // Commit final state message for stream 2 - time to commit is 12 seconds (second 14 - second 02)
    stateMetricsTracker.incrementTotalDestinationEmittedStateMessages();
    stateMetricsTracker.updateStates(s2s2, 2, LocalDateTime.parse("2022-01-01 12:00:14", FORMATTER));

    // max time across both streams was 12, mean time across all streams was (5 + 7 + 12)/3 == 24/3 == 8
    assertEquals(12L, stateMetricsTracker.getMaxSecondsBetweenStateMessageEmittedAndCommitted());
    assertEquals(8L, stateMetricsTracker.getMeanSecondsBetweenStateMessageEmittedAndCommitted());
  }

  @Test
  void testGlobalMaxandMeanSecondsBetweenStateMessageEmittedandCommitted()
      throws StateMetricsTrackerOomException, StateMetricsTrackerNoStateMatchException {
    final AirbyteMessage s1 = AirbyteMessageUtils.createGlobalStateMessage(1, STREAM_1);
    final AirbyteMessage s2 = AirbyteMessageUtils.createGlobalStateMessage(2, STREAM_1);
    final AirbyteMessage s3 = AirbyteMessageUtils.createGlobalStateMessage(3, STREAM_1);

    // 3 global state messages emitted
    stateMetricsTracker.addState(s1.getState(), 0, LocalDateTime.parse(SECOND_ZERO, FORMATTER));
    stateMetricsTracker.addState(s2.getState(), 1, LocalDateTime.parse(SECOND_ONE, FORMATTER));
    stateMetricsTracker.addState(s3.getState(), 2, LocalDateTime.parse(SECOND_TWO, FORMATTER));

    // Committed up to 2nd state message - time to commit is 5 seconds (second 00 to second 05)
    stateMetricsTracker.incrementTotalDestinationEmittedStateMessages();
    stateMetricsTracker.updateStates(s2.getState(), 1, LocalDateTime.parse(SECOND_FIVE, FORMATTER));

    // Committed final state message - time to commit is 7 seconds (second 02 to second 09)
    stateMetricsTracker.incrementTotalDestinationEmittedStateMessages();
    stateMetricsTracker.updateStates(s3.getState(), 2, LocalDateTime.parse("2022-01-01 12:00:09", FORMATTER));

    assertEquals(7L, stateMetricsTracker.getMaxSecondsBetweenStateMessageEmittedAndCommitted());
    assertEquals(6L, stateMetricsTracker.getMeanSecondsBetweenStateMessageEmittedAndCommitted());
  }

  @Test
  void testStateMetricsTrackerOomExceptionThrown() throws StateMetricsTrackerOomException {
    final StateMetricsTracker stateMetricsTrackerOom = new StateMetricsTracker(2L);

    final AirbyteMessage s1 = AirbyteMessageUtils.createGlobalStateMessage(1, STREAM_1);
    final AirbyteMessage s2 = AirbyteMessageUtils.createGlobalStateMessage(2, STREAM_1);
    final AirbyteMessage s3 = AirbyteMessageUtils.createGlobalStateMessage(3, STREAM_1);

    // 3 global state messages emitted
    stateMetricsTrackerOom.addState(s1.getState(), 0, LocalDateTime.parse(SECOND_ZERO, FORMATTER));
    stateMetricsTrackerOom.addState(s2.getState(), 1, LocalDateTime.parse(SECOND_ONE, FORMATTER));

    assertThrows(StateMetricsTrackerOomException.class,
        () -> stateMetricsTrackerOom.addState(s3.getState(), 2, LocalDateTime.parse(SECOND_TWO, FORMATTER)));

  }

  @Test
  void testStateMetricsTrackerNoStateMatchExceptionThrown() throws StateMetricsTrackerNoStateMatchException, StateMetricsTrackerOomException {
    final AirbyteMessage s1 = AirbyteMessageUtils.createGlobalStateMessage(1, STREAM_1);
    final AirbyteMessage s2 = AirbyteMessageUtils.createGlobalStateMessage(2, STREAM_1);
    final AirbyteMessage s3 = AirbyteMessageUtils.createGlobalStateMessage(3, STREAM_1);

    // destination emits state message hash when there are no source state message hashes stored
    stateMetricsTracker.incrementTotalDestinationEmittedStateMessages();
    assertThrows(StateMetricsTrackerNoStateMatchException.class,
        () -> stateMetricsTracker.updateStates(s1.getState(), 4, LocalDateTime.parse(SECOND_FIVE, FORMATTER)));

    stateMetricsTracker.addState(s1.getState(), 0, LocalDateTime.parse(SECOND_ZERO, FORMATTER));
    stateMetricsTracker.addState(s2.getState(), 1, LocalDateTime.parse(SECOND_ONE, FORMATTER));
    stateMetricsTracker.addState(s3.getState(), 2, LocalDateTime.parse(SECOND_TWO, FORMATTER));

    // destination emits a state message hash that does not correspond to any source state message
    // hashes
    assertThrows(StateMetricsTrackerNoStateMatchException.class,
        () -> stateMetricsTracker.updateStates(s3.getState(), 4, LocalDateTime.parse(SECOND_FIVE, FORMATTER)));
  }

  @Test
  void testStreamMaxandMeanSecondsBeforeStateMessageEmitted() {
    // first record received at second 0
    stateMetricsTracker.setFirstRecordReceivedAt(LocalDateTime.parse(SECOND_ZERO, FORMATTER));

    // receive state at second 2
    stateMetricsTracker.incrementTotalSourceEmittedStateMessages();
    stateMetricsTracker.updateMaxAndMeanSecondsToReceiveStateMessage(LocalDateTime.parse(SECOND_TWO, FORMATTER));
    stateMetricsTracker.setLastStateMessageReceivedAt(LocalDateTime.parse(SECOND_TWO, FORMATTER));
    // max and mean seconds to receive state message are both 2 seconds
    assertEquals(2L, stateMetricsTracker.getMaxSecondsToReceiveSourceStateMessage());
    assertEquals(2L, stateMetricsTracker.getMeanSecondsToReceiveSourceStateMessage());

    // another state message received after 4 more seconds
    stateMetricsTracker.incrementTotalSourceEmittedStateMessages();
    stateMetricsTracker.updateMaxAndMeanSecondsToReceiveStateMessage(LocalDateTime.parse(SECOND_SIX, FORMATTER));
    stateMetricsTracker.setLastStateMessageReceivedAt(LocalDateTime.parse(SECOND_SIX, FORMATTER));

    // max and mean seconds to receive state message are both 2 seconds
    assertEquals(4L, stateMetricsTracker.getMaxSecondsToReceiveSourceStateMessage());
    assertEquals(3L, stateMetricsTracker.getMeanSecondsToReceiveSourceStateMessage());
  }

}
