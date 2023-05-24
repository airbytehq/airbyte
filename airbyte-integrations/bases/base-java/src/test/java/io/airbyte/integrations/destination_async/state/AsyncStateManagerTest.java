/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.buffers.BufferManager;
import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class AsyncStateManagerTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = STREAM_NAME + 2;
  private static final StreamDescriptor STREAM1_DESC = new StreamDescriptor()
      .withName(STREAM_NAME);
  private static final StreamDescriptor STREAM2_DESC = new StreamDescriptor()
      .withName(STREAM_NAME2);

  private static final AirbyteMessage GLOBAL_MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.GLOBAL));
  private static final AirbyteMessage STREAM1_STATE_MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState().withStreamDescriptor(STREAM1_DESC).withStreamState(Jsons.jsonNode(1))));
  private static final AirbyteMessage STREAM1_STATE_MESSAGE2 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState().withStreamDescriptor(STREAM1_DESC).withStreamState(Jsons.jsonNode(2))));


  @Test
  void testBasic() {
    final AsyncStateManager stateManager = new AsyncStateManager();

    final var firstStateId = stateManager.getStateIdAndIncrement(STREAM1_DESC);
    final var secondStateId = stateManager.getStateIdAndIncrement(STREAM1_DESC);
    assertEquals(firstStateId, secondStateId);

    stateManager.decrement(firstStateId, 2);
    // because no state message has been tracked, there is nothing to flush yet.
    var flushed = stateManager.flushStates();
    assertEquals(0, flushed.size());

    stateManager.trackState(STREAM1_STATE_MESSAGE1);
    flushed = stateManager.flushStates();
    assertEquals(List.of(STREAM1_STATE_MESSAGE1), flushed);
  }

  @Nested
  class GlobalState {
    @Test
    void testEmptyQueuesGlobalState() {
      final AsyncStateManager stateManager = new AsyncStateManager();

      // GLOBAL
      stateManager.trackState(GLOBAL_MESSAGE1);
      assertEquals(List.of(GLOBAL_MESSAGE1), stateManager.flushStates());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(STREAM1_STATE_MESSAGE1));
    }
  }

  @Nested
  class PerStreamState {
    @Test
    void testEmptyQueues() {
      final AsyncStateManager stateManager = new AsyncStateManager();

      // GLOBAL
      stateManager.trackState(STREAM1_STATE_MESSAGE1);
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateManager.flushStates());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(GLOBAL_MESSAGE1));
    }

    @Test
    void testCorrectFlushingOneStream() {
      final AsyncStateManager stateManager = new AsyncStateManager();

      var stateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE1);
      stateManager.decrement(stateId, 3);
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateManager.flushStates());

      stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE2);
      stateManager.decrement(stateId, 10);
      assertEquals(List.of(STREAM1_STATE_MESSAGE2), stateManager.flushStates());

    }

    @Test
    void testCorrectFlushingManyStream() {
      final AsyncStateManager stateManager = new AsyncStateManager();

      final var stream1StateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      final var stream2StateId = simulateIncomingRecords(STREAM2_DESC, 7, stateManager);

      stateManager.trackState(STREAM1_STATE_MESSAGE1);
      stateManager.decrement(stream1StateId, 3);
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateManager.flushStates());

      stateManager.decrement(stream2StateId, 4);
      assertEquals(List.of(), stateManager.flushStates());
      stateManager.trackState(STREAM1_STATE_MESSAGE2);
      stateManager.decrement(stream2StateId, 3);
      assertEquals(List.of(STREAM1_STATE_MESSAGE2), stateManager.flushStates());
    }
  }

  @Test
  void testStateAcrossMultipleStreams() {
    final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers = new ConcurrentHashMap<>();
    buffers.put(STREAM1_DESC, new StreamAwareQueue(BufferManager.TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));
    buffers.put(STREAM2_DESC, new StreamAwareQueue(BufferManager.TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));
    final AsyncStateManager stateManager = new AsyncStateManager();

//    final List<AirbyteMessage> stream1Records = generateRecords(1000, STREAM_NAME);
//    long count = 0;
//    for (final AirbyteMessage r : stream1Records) {
//      buffers.get(STREAM1_DESC).offer(r, count++, 160);
//    }
//
//    final List<AirbyteMessage> stream2Records = generateRecords(1000, STREAM_NAME2);
//    for (final AirbyteMessage r : stream2Records) {
//      if (count % 1120 == 0) {
//        stateManager.trackState(GLOBAL_MESSAGE1);
//      }
//      buffers.get(STREAM2_DESC).offer(r, count++, 160);
//    }

    // stateManager.claim(STREAM2_DESC, 1500);
    // drainNRecords(buffers, STREAM2_DESC, 500);
    // assertEquals(Optional.empty(), stateManager.fulfill(STREAM2_DESC, 1500));
    //
    // stateManager.claim(STREAM1_DESC, 900);
    // drainNRecords(buffers, STREAM1_DESC, 900);
    // assertEquals(Optional.empty(), stateManager.fulfill(STREAM1_DESC, 900));
    //
    // stateManager.claim(STREAM1_DESC, 1000);
    // drainNRecords(buffers, STREAM1_DESC, 100);
    // assertEquals(Optional.of(GLOBAL_MESSAGE1), stateManager.fulfill(STREAM1_DESC, 1000));
  }

  @Test
  void testOutOfOrderFulfills() {
    final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers = new ConcurrentHashMap<>();
    buffers.put(STREAM1_DESC, new StreamAwareQueue(BufferManager.TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));
    final AsyncStateManager stateManager = new AsyncStateManager();

//    final List<AirbyteMessage> stream1Records = generateRecords(1000, STREAM_NAME);
//    long count = 0;
//    for (final AirbyteMessage r : stream1Records) {
//      if (count > 0 && count % 950 == 0) {
//        stateManager.trackState(GLOBAL_MESSAGE1);
//      }
//      buffers.get(STREAM1_DESC).offer(r, count++, 160);
//    }

    // worker 1
    // stateManager.claim(STREAM1_DESC, 900);
    drainNRecords(buffers, STREAM1_DESC, 900);
    // worker 2
    // stateManager.claim(STREAM1_DESC, 1001);
    drainNRecords(buffers, STREAM1_DESC, 100);

    // assertEquals(Optional.empty(), stateManager.fulfill(STREAM1_DESC, 1001));
    // assertEquals(Optional.of(GLOBAL_MESSAGE1), stateManager.fulfill(STREAM1_DESC, 900));
  }

  void drainNRecords(final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers,
                     final StreamDescriptor streamDescriptor,
                     final int numRecord) {

    for (int i = 0; i < numRecord; i++) {
      buffers.get(streamDescriptor).poll();
    }
  }

  private static long simulateIncomingRecords(final StreamDescriptor desc, final long count, final AsyncStateManager manager) {
    var stateId = 0L;
    for (int i = 0; i < count; i++) {
      stateId = manager.getStateIdAndIncrement(desc);
    }
    return stateId;
  }
}
