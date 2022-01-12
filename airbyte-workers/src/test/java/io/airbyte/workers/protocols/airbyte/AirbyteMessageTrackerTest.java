/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.workers.protocols.airbyte.StateDeltaTracker.StateDeltaTrackerException;
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

  private AirbyteMessageTracker messageTracker;

  @Mock
  private StateDeltaTracker mStateDeltaTracker;

  @BeforeEach
  public void setup() {
    this.messageTracker = new AirbyteMessageTracker(mStateDeltaTracker);
  }

  @Test
  public void testGetTotalRecordsStatesAndBytesEmitted() {
    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 123);
    final AirbyteMessage s1 = createStateMessage(1);
    final AirbyteMessage s2 = createStateMessage(2);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromSource(s2);

    assertEquals(3, messageTracker.getTotalRecordsEmitted());
    assertEquals(3 * Jsons.serialize(r1.getRecord().getData()).getBytes(Charsets.UTF_8).length, messageTracker.getTotalBytesEmitted());
    assertEquals(2, messageTracker.getTotalStateMessagesEmitted());
  }

  @Test
  public void testRetainsLatestSourceAndDestinationState() {
    final int s1Value = 111;
    final int s2Value = 222;
    final int s3Value = 333;
    final AirbyteMessage s1 = createStateMessage(s1Value);
    final AirbyteMessage s2 = createStateMessage(s2Value);
    final AirbyteMessage s3 = createStateMessage(s3Value);

    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromSource(s2);
    messageTracker.acceptFromSource(s3);
    messageTracker.acceptFromDestination(s1);
    messageTracker.acceptFromDestination(s2);

    assertTrue(messageTracker.getSourceOutputState().isPresent());
    assertEquals(new State().withState(Jsons.jsonNode(s3Value)), messageTracker.getSourceOutputState().get());

    assertTrue(messageTracker.getDestinationOutputState().isPresent());
    assertEquals(new State().withState(Jsons.jsonNode(s2Value)), messageTracker.getDestinationOutputState().get());
  }

  @Test
  public void testReturnEmptyStateIfNoneEverAccepted() {
    assertTrue(messageTracker.getSourceOutputState().isEmpty());
    assertTrue(messageTracker.getDestinationOutputState().isEmpty());
  }

  @Test
  public void testEmittedRecordsByStream() {
    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = createRecordMessage(STREAM_3, 3);

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
  public void testEmittedBytesByStream() {
    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = createRecordMessage(STREAM_3, 3);

    final long r1Bytes = Jsons.serialize(r1.getRecord().getData()).getBytes(Charsets.UTF_8).length;
    final long r2Bytes = Jsons.serialize(r2.getRecord().getData()).getBytes(Charsets.UTF_8).length;
    final long r3Bytes = Jsons.serialize(r3.getRecord().getData()).getBytes(Charsets.UTF_8).length;

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
  public void testGetCommittedRecordsByStream() {
    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = createRecordMessage(STREAM_3, 3);
    final AirbyteMessage s1 = createStateMessage(1);
    final AirbyteMessage s2 = createStateMessage(2);

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
  public void testGetCommittedRecordsByStream_emptyWhenAddStateThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException("induced exception")).when(mStateDeltaTracker).addState(Mockito.anyInt(), Mockito.anyMap());

    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getStreamToCommittedRecords().isEmpty());
  }

  @Test
  public void testGetCommittedRecordsByStream_emptyWhenCommitStateHashThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException("induced exception")).when(mStateDeltaTracker).commitStateHash(Mockito.anyInt());

    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getStreamToCommittedRecords().isEmpty());
  }

  @Test
  public void testTotalRecordsCommitted() {
    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage r2 = createRecordMessage(STREAM_2, 2);
    final AirbyteMessage r3 = createRecordMessage(STREAM_3, 3);
    final AirbyteMessage s1 = createStateMessage(1);
    final AirbyteMessage s2 = createStateMessage(2);

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
  public void testGetTotalRecordsCommitted_emptyWhenAddStateThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException("induced exception")).when(mStateDeltaTracker).addState(Mockito.anyInt(), Mockito.anyMap());

    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getTotalRecordsCommitted().isEmpty());
  }

  @Test
  public void testGetTotalRecordsCommitted_emptyWhenCommitStateHashThrowsException() throws Exception {
    Mockito.doThrow(new StateDeltaTrackerException("induced exception")).when(mStateDeltaTracker).commitStateHash(Mockito.anyInt());

    final AirbyteMessage r1 = createRecordMessage(STREAM_1, 1);
    final AirbyteMessage s1 = createStateMessage(1);

    messageTracker.acceptFromSource(r1);
    messageTracker.acceptFromSource(s1);
    messageTracker.acceptFromDestination(s1);

    assertTrue(messageTracker.getTotalRecordsCommitted().isEmpty());
  }

  private AirbyteMessage createRecordMessage(final String streamName, final int recordData) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withData(Jsons.jsonNode(recordData)));
  }

  private AirbyteMessage createStateMessage(final int stateData) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(stateData)));
  }

}
