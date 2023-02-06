/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.book_keeping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.FailureReason;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.internal.book_keeping.StateDeltaTracker.StateDeltaTrackerException;
import io.airbyte.workers.internal.state_aggregator.StateAggregator;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AirbyteMessageTrackerTest {

  private static final String NAMESPACE_1 = "avengers";
  private static final String STREAM_1 = "iron man";
  private static final String STREAM_2 = "black widow";
  private static final String STREAM_3 = "hulk";
  private static final String INDUCED_EXCEPTION = "induced exception";

  private AirbyteMessageTracker messageTracker;

  @Mock
  private StateDeltaTracker mStateDeltaTracker;

  @Mock
  private StateAggregator mStateAggregator;

  @BeforeEach
  void setup() {
    final StateMetricsTracker stateMetricsTracker = new StateMetricsTracker(10L * 1024L * 1024L);
    this.messageTracker = new AirbyteMessageTracker(mStateDeltaTracker, mStateAggregator, stateMetricsTracker, new EnvVariableFeatureFlags());
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

    final HashMap<AirbyteStreamNameNamespacePair, Long> expected = new HashMap<>();
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r1.getRecord()), 1L);
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r2.getRecord()), 2L);
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r3.getRecord()), 3L);

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

    final Map<AirbyteStreamNameNamespacePair, Long> expected = new HashMap<>();
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r1.getRecord()), r1Bytes);
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r2.getRecord()), r2Bytes * 2);
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r3.getRecord()), r3Bytes * 3);

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
    final Map<AirbyteStreamNameNamespacePair, Long> expected = new HashMap<>();
    Mockito.when(mStateDeltaTracker.getStreamToCommittedRecords()).thenReturn(countsByIndex);

    countsByIndex.put((short) 0, 1L);
    countsByIndex.put((short) 1, 2L);
    // result only contains counts up to state 1
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r1.getRecord()), 1L);
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r2.getRecord()), 2L);
    assertEquals(expected, messageTracker.getStreamToCommittedRecords().get());

    countsByIndex.clear();
    expected.clear();
    messageTracker.acceptFromDestination(s2); // now commit state 2
    countsByIndex.put((short) 0, 3L);
    countsByIndex.put((short) 1, 3L);
    countsByIndex.put((short) 2, 1L);
    // result updated with counts between state 1 and state 2
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r1.getRecord()), 3L);
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r2.getRecord()), 3L);
    expected.put(AirbyteStreamNameNamespacePair.fromRecordMessage(r3.getRecord()), 1L);
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
  void testGetFirstDestinationAndSourceMessages() {
    final AirbyteMessage sourceMessage1 = AirbyteMessageUtils.createErrorMessage("source trace 1", 123.0);
    final AirbyteMessage sourceMessage2 = AirbyteMessageUtils.createErrorMessage("source trace 2", 124.0);
    final AirbyteMessage destMessage1 = AirbyteMessageUtils.createErrorMessage("dest trace 1", 125.0);
    final AirbyteMessage destMessage2 = AirbyteMessageUtils.createErrorMessage("dest trace 2", 126.0);
    messageTracker.acceptFromSource(sourceMessage1);
    messageTracker.acceptFromSource(sourceMessage2);
    messageTracker.acceptFromDestination(destMessage1);
    messageTracker.acceptFromDestination(destMessage2);

    assertEquals(messageTracker.getFirstDestinationErrorTraceMessage(), destMessage1.getTrace());
    assertEquals(messageTracker.getFirstSourceErrorTraceMessage(), sourceMessage1.getTrace());
  }

  @Test
  void testGetFirstDestinationAndSourceMessagesWithNulls() {
    assertNull(messageTracker.getFirstDestinationErrorTraceMessage());
    assertNull(messageTracker.getFirstSourceErrorTraceMessage());
  }

  @Test
  void testErrorTraceMessageFailureWithMultipleTraceErrors() {
    final AirbyteMessage sourceMessage1 = AirbyteMessageUtils.createErrorMessage("source trace 1", 123.0);
    final AirbyteMessage sourceMessage2 = AirbyteMessageUtils.createErrorMessage("source trace 2", 124.0);
    final AirbyteMessage destMessage1 = AirbyteMessageUtils.createErrorMessage("dest trace 1", 125.0);
    final AirbyteMessage destMessage2 = AirbyteMessageUtils.createErrorMessage("dest trace 2", 126.0);
    messageTracker.acceptFromSource(sourceMessage1);
    messageTracker.acceptFromSource(sourceMessage2);
    messageTracker.acceptFromDestination(destMessage1);
    messageTracker.acceptFromDestination(destMessage2);

    final FailureReason failureReason = FailureHelper.sourceFailure(sourceMessage1.getTrace(), Long.valueOf(123), 1);
    assertEquals(messageTracker.errorTraceMessageFailure(123L, 1),
        failureReason);
  }

  @Test
  void testErrorTraceMessageFailureWithOneTraceError() {
    final AirbyteMessage destMessage = AirbyteMessageUtils.createErrorMessage("dest trace 1", 125.0);
    messageTracker.acceptFromDestination(destMessage);

    final FailureReason failureReason = FailureHelper.destinationFailure(destMessage.getTrace(), Long.valueOf(123), 1);
    assertEquals(messageTracker.errorTraceMessageFailure(123L, 1), failureReason);
  }

  @Test
  void testErrorTraceMessageFailureWithNoTraceErrors() {
    assertEquals(messageTracker.errorTraceMessageFailure(123L, 1), null);
  }

  @Nested
  class Estimates {

    // receiving an estimate for two streams should save
    @Test
    @DisplayName("when given stream estimates, should return correct per-stream estimates")
    void streamShouldSaveAndReturnIndividualStreamCountsCorrectly() {
      final var est1 = AirbyteMessageUtils.createStreamEstimateMessage(STREAM_1, NAMESPACE_1, 100L, 10L);
      final var est2 = AirbyteMessageUtils.createStreamEstimateMessage(STREAM_2, NAMESPACE_1, 200L, 10L);

      messageTracker.acceptFromSource(est1);
      messageTracker.acceptFromSource(est2);

      final var streamToEstBytes = messageTracker.getStreamToEstimatedBytes();
      final var expStreamToEstBytes = Map.of(
          new AirbyteStreamNameNamespacePair(STREAM_1, NAMESPACE_1), 100L,
          new AirbyteStreamNameNamespacePair(STREAM_2, NAMESPACE_1), 200L);
      assertEquals(expStreamToEstBytes, streamToEstBytes);

      final var streamToEstRecs = messageTracker.getStreamToEstimatedRecords();
      final var expStreamToEstRecs = Map.of(
          new AirbyteStreamNameNamespacePair(STREAM_1, NAMESPACE_1), 10L,
          new AirbyteStreamNameNamespacePair(STREAM_2, NAMESPACE_1), 10L);
      assertEquals(expStreamToEstRecs, streamToEstRecs);
    }

    @Test
    @DisplayName("when given stream estimates, should return correct total estimates")
    void streamShouldSaveAndReturnTotalCountsCorrectly() {
      final var est1 = AirbyteMessageUtils.createStreamEstimateMessage(STREAM_1, NAMESPACE_1, 100L, 10L);
      final var est2 = AirbyteMessageUtils.createStreamEstimateMessage(STREAM_2, NAMESPACE_1, 200L, 10L);

      messageTracker.acceptFromSource(est1);
      messageTracker.acceptFromSource(est2);

      final var totalEstBytes = messageTracker.getTotalBytesEstimated();
      assertEquals(300L, totalEstBytes);

      final var totalEstRecs = messageTracker.getTotalRecordsEstimated();
      assertEquals(20L, totalEstRecs);
    }

    @Test
    @DisplayName("should error when given both Stream and Sync estimates")
    void shouldErrorOnBothStreamAndSyncEstimates() {
      final var est1 = AirbyteMessageUtils.createStreamEstimateMessage(STREAM_1, NAMESPACE_1, 100L, 10L);
      final var est2 = AirbyteMessageUtils.createSyncEstimateMessage(200L, 10L);

      messageTracker.acceptFromSource(est1);
      assertThrows(IllegalArgumentException.class, () -> messageTracker.acceptFromSource(est2));
    }

    @Test
    @DisplayName("when given sync estimates, should return correct total estimates")
    void syncShouldSaveAndReturnTotalCountsCorrectly() {
      final var est = AirbyteMessageUtils.createSyncEstimateMessage(200L, 10L);
      messageTracker.acceptFromSource(est);

      final var totalEstBytes = messageTracker.getTotalBytesEstimated();
      assertEquals(200L, totalEstBytes);

      final var totalEstRecs = messageTracker.getTotalRecordsEstimated();
      assertEquals(10L, totalEstRecs);
    }

    @Test
    @DisplayName("when given sync estimates, should not return any per-stream estimates")
    void syncShouldNotHaveStreamEstimates() {
      final var est = AirbyteMessageUtils.createSyncEstimateMessage(200L, 10L);
      messageTracker.acceptFromSource(est);

      final var streamToEstBytes = messageTracker.getStreamToEstimatedBytes();
      assertTrue(streamToEstBytes.isEmpty());
      final var streamToEstRecs = messageTracker.getStreamToEstimatedRecords();
      assertTrue(streamToEstRecs.isEmpty());
    }

  }

}
