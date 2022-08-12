/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.FailureReason;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.internal.StateDeltaTracker.StateDeltaTrackerException;
import io.airbyte.workers.internal.state_aggregator.StateAggregator;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AirbyteMessageTrackerTest {

  private static final String STREAM_1 = "stream1";
  private static final String STREAM_2 = "stream2";
  private static final String STREAM_3 = "stream3";
  private static final String INDUCED_EXCEPTION = "induced exception";

  private AirbyteMessageTracker messageTracker;

  @Mock
  private StateDeltaTracker mStateDeltaTracker;

  @Mock
  private StateAggregator mStateAggregator;

  @BeforeEach
  void setup() {
    this.messageTracker = new AirbyteMessageTracker(mStateDeltaTracker, mStateAggregator);
  }

  @Test
  void testGetTotalRecordsStatesAndBytesEmitted() {
    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 123);
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(1);
    final AirbyteMessage s2 = AirbyteMessageUtils.createStateMessage(2);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromSource(s2);

    assertEquals(3, messageTracker.getTotalRecordsEmitted());
    assertEquals(3L * Jsons.getEstimatedByteSize(r1.getRecord().getData()), messageTracker.getTotalBytesEmitted());
    assertEquals(2, messageTracker.getTotalSourceStateMessagesEmitted());
  }

  @Test
  void testRetainsLatestSourceAndDestinationState() {
    final int s1Value = 111;
    final int s2Value = 222;
    final int s3Value = 333;
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(s1Value);
    final AirbyteMessage s2 = AirbyteMessageUtils.createStateMessage(s2Value);
    final AirbyteMessage s3 = AirbyteMessageUtils.createStateMessage(s3Value);

    final State expectedState = new State().withState(Jsons.jsonNode(s2Value));
    Mockito.when(mStateAggregator.getAggregated()).thenReturn(expectedState);

    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromSource(s2);
    messageTracker.acceptFromSource(s3);
    messageTracker.acceptFromDestination(s1);
    messageTracker.acceptFromDestination(s2);

    assertTrue(messageTracker.getSourceOutputState().isPresent());
    assertEquals(new State().withState(Jsons.jsonNode(s3Value)), messageTracker.getSourceOutputState().get());

    assertTrue(messageTracker.getDestinationOutputState().isPresent());
    assertEquals(expectedState, messageTracker.getDestinationOutputState().get());
  }

  @Test
  void testReturnEmptyStateIfNoneEverAccepted() {
    assertTrue(messageTracker.getSourceOutputState().isEmpty());
    assertTrue(messageTracker.getDestinationOutputState().isEmpty());
  }

  @Test
  void testEmittedRecordsByStream() {
    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = AirbyteMessageUtils.createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = AirbyteMessageUtils.createRecordMessage(STREAM_3, 3);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromSource(r3);
    messageTracker.acceptFromSource(r3);
    messageTracker.acceptFromSource(r3);

    final Map<String, Long> expected = new HashMap<>();
    expected.put(STREAM_1, 1L);
    expected.put(STREAM_2, 2L);
    expected.put(STREAM_3, 3L);

    assertEquals(expected, messageTracker.getStreamToEmittedRecords());
  }

  @Test
  void testEmittedBytesByStream() {
    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = AirbyteMessageUtils.createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = AirbyteMessageUtils.createRecordMessage(STREAM_3, 3);

    final long r1Bytes = Jsons.getEstimatedByteSize(r1.getRecord().getData());
    final long r2Bytes = Jsons.getEstimatedByteSize(r2.getRecord().getData());
    final long r3Bytes = Jsons.getEstimatedByteSize(r3.getRecord().getData());

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromSource(r3);
    messageTracker.acceptFromSource(r3);
    messageTracker.acceptFromSource(r3);

    final Map<String, Long> expected = new HashMap<>();
    expected.put(STREAM_1, r1Bytes);
    expected.put(STREAM_2, r2Bytes * 2);
    expected.put(STREAM_3, r3Bytes * 3);

    assertEquals(expected, messageTracker.getStreamToEmittedBytes());
  }

  @Test
  void testGetCommittedRecordsByStream() {
    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = AirbyteMessageUtils.createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = AirbyteMessageUtils.createRecordMessage(STREAM_3, 3);
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(1);
    final AirbyteMessage s2 = AirbyteMessageUtils.createStateMessage(2);

    messageTracker.acceptFromSource(r1); // should make stream 1 index 0
    messageTracker.acceptFromSource(r2); // should make stream 2 index 1
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromSource(s1); // emit state 1
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromDestination(s1); // commit state 1
    messageTracker.acceptFromSource(r3); // should make stream 3 index 2
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s2); // emit state 2

    final Map<Short, Long> countsByIndex = new HashMap<>();
    final Map<String, Long> expected = new HashMap<>();
    Mockito.when(mStateDeltaTracker.getStreamToCommittedRecords()).thenReturn(countsByIndex);

    countsByIndex.put((short) 0, 1L);
    countsByIndex.put((short) 1, 2L);
    // result only contains counts up to state 1
    expected.put(STREAM_1, 1L);
    expected.put(STREAM_2, 2L);
    assertEquals(expected, messageTracker.getStreamToCommittedRecords().get());

    countsByIndex.clear();
    expected.clear();
    messageTracker.acceptFromDestination(s2); // now commit state 2
    countsByIndex.put((short) 0, 3L);
    countsByIndex.put((short) 1, 3L);
    countsByIndex.put((short) 2, 1L);
    // result updated with counts between state 1 and state 2
    expected.put(STREAM_1, 3L);
    expected.put(STREAM_2, 3L);
    expected.put(STREAM_3, 1L);
    assertEquals(expected, messageTracker.getStreamToCommittedRecords().get());
  }

  @Test
  void testGetCommittedRecordsByStream_emptyWhenAddStateThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException(INDUCED_EXCEPTION)).when(mStateDeltaTracker).addState(Mockito.anyInt(), Mockito.anyMap());

    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getStreamToCommittedRecords().isEmpty());
  }

  @Test
  void testGetCommittedRecordsByStream_emptyWhenCommitStateHashThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException(INDUCED_EXCEPTION)).when(mStateDeltaTracker).commitStateHash(Mockito.anyInt());

    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getStreamToCommittedRecords().isEmpty());
  }

  @Test
  void testTotalRecordsCommitted() {
    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = AirbyteMessageUtils.createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = AirbyteMessageUtils.createRecordMessage(STREAM_3, 3);
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(1);
    final AirbyteMessage s2 = AirbyteMessageUtils.createStateMessage(2);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromSource(s1); // emit state 1
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r2);
    messageTracker.acceptFromDestination(s1); // commit state 1
    messageTracker.acceptFromSource(r3);
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s2); // emit state 2

    final Map<Short, Long> countsByIndex = new HashMap<>();
    Mockito.when(mStateDeltaTracker.getStreamToCommittedRecords()).thenReturn(countsByIndex);

    countsByIndex.put((short) 0, 1L);
    countsByIndex.put((short) 1, 2L);
    // result only contains counts up to state 1
    assertEquals(3L, messageTracker.getTotalRecordsCommitted().get());

    countsByIndex.clear();
    messageTracker.acceptFromDestination(s2); // now commit state 2
    countsByIndex.put((short) 0, 3L);
    countsByIndex.put((short) 1, 3L);
    countsByIndex.put((short) 2, 1L);
    // result updated with counts between state 1 and state 2
    assertEquals(7L, messageTracker.getTotalRecordsCommitted().get());
  }

  @Test
  void testGetTotalRecordsCommitted_emptyWhenAddStateThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException(INDUCED_EXCEPTION)).when(mStateDeltaTracker).addState(Mockito.anyInt(), Mockito.anyMap());

    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getTotalRecordsCommitted().isEmpty());
  }

  @Test
  void testGetTotalRecordsCommitted_emptyWhenCommitStateHashThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException(INDUCED_EXCEPTION)).when(mStateDeltaTracker).commitStateHash(Mockito.anyInt());

    final AirbyteMessage r1 = AirbyteMessageUtils.createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = AirbyteMessageUtils.createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getTotalRecordsCommitted().isEmpty());
  }

  @Test
  void testGetFirstDestinationAndSourceMessages() throws Exception {
    final AirbyteMessage sourceMessage1 = AirbyteMessageUtils.createTraceMessage("source trace 1", Double.valueOf(123));
    final AirbyteMessage sourceMessage2 = AirbyteMessageUtils.createTraceMessage("source trace 2", Double.valueOf(124));
    final AirbyteMessage destMessage1 = AirbyteMessageUtils.createTraceMessage("dest trace 1", Double.valueOf(125));
    final AirbyteMessage destMessage2 = AirbyteMessageUtils.createTraceMessage("dest trace 2", Double.valueOf(126));
    messageTracker.acceptFromSource(sourceMessage1);
    messageTracker.acceptFromSource(sourceMessage2);
    messageTracker.acceptFromDestination(destMessage1);
    messageTracker.acceptFromDestination(destMessage2);

    assertEquals(messageTracker.getFirstDestinationErrorTraceMessage(), destMessage1.getTrace());
    assertEquals(messageTracker.getFirstSourceErrorTraceMessage(), sourceMessage1.getTrace());
  }

  @Test
  void testGetFirstDestinationAndSourceMessagesWithNulls() throws Exception {
    assertEquals(messageTracker.getFirstDestinationErrorTraceMessage(), null);
    assertEquals(messageTracker.getFirstSourceErrorTraceMessage(), null);
  }

  @Test
  void testErrorTraceMessageFailureWithMultipleTraceErrors() throws Exception {
    final AirbyteMessage sourceMessage1 = AirbyteMessageUtils.createTraceMessage("source trace 1", Double.valueOf(123));
    final AirbyteMessage sourceMessage2 = AirbyteMessageUtils.createTraceMessage("source trace 2", Double.valueOf(124));
    final AirbyteMessage destMessage1 = AirbyteMessageUtils.createTraceMessage("dest trace 1", Double.valueOf(125));
    final AirbyteMessage destMessage2 = AirbyteMessageUtils.createTraceMessage("dest trace 2", Double.valueOf(126));
    messageTracker.acceptFromSource(sourceMessage1);
    messageTracker.acceptFromSource(sourceMessage2);
    messageTracker.acceptFromDestination(destMessage1);
    messageTracker.acceptFromDestination(destMessage2);

    final FailureReason failureReason = FailureHelper.sourceFailure(sourceMessage1.getTrace(), Long.valueOf(123), 1);
    assertEquals(messageTracker.errorTraceMessageFailure(Long.valueOf(123), 1),
        failureReason);
  }

  @Test
  void testErrorTraceMessageFailureWithOneTraceError() throws Exception {
    final AirbyteMessage destMessage = AirbyteMessageUtils.createTraceMessage("dest trace 1", Double.valueOf(125));
    messageTracker.acceptFromDestination(destMessage);

    final FailureReason failureReason = FailureHelper.destinationFailure(destMessage.getTrace(), Long.valueOf(123), 1);
    assertEquals(messageTracker.errorTraceMessageFailure(Long.valueOf(123), 1), failureReason);
  }

  @Test
  void testErrorTraceMessageFailureWithNoTraceErrors() throws Exception {
    assertEquals(messageTracker.errorTraceMessageFailure(Long.valueOf(123), 1), null);
  }

}
