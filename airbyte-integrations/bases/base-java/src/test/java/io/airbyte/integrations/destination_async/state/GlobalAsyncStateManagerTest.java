/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteStateMessage;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteStreamState;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class GlobalAsyncStateManagerTest {

  private static final long TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = 100 * 1024 * 1024; // 10MB

  private static final long STATE_MSG_SIZE = 1000;

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = STREAM_NAME + 2;
  private static final String STREAM_NAME3 = STREAM_NAME + 3;
  private static final StreamDescriptor STREAM1_DESC = new StreamDescriptor()
      .withName(STREAM_NAME);
  private static final StreamDescriptor STREAM2_DESC = new StreamDescriptor()
      .withName(STREAM_NAME2);
  private static final StreamDescriptor STREAM3_DESC = new StreamDescriptor()
      .withName(STREAM_NAME3);

  private static final PartialAirbyteMessage GLOBAL_STATE_MESSAGE1 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.GLOBAL));
  private static final PartialAirbyteMessage GLOBAL_STATE_MESSAGE2 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.GLOBAL));
  private static final PartialAirbyteMessage STREAM1_STATE_MESSAGE1 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)));
  private static final PartialAirbyteMessage STREAM1_STATE_MESSAGE2 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)));

  @Test
  void testBasic() {
    final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

    final var firstStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC);
    final var secondStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC);
    assertEquals(firstStateId, secondStateId);

    stateManager.decrement(firstStateId, 2);
    // because no state message has been tracked, there is nothing to flush yet.
    var flushed = stateManager.flushStates();
    assertEquals(0, flushed.size());

    stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE);
    flushed = stateManager.flushStates();
    assertEquals(List.of(STREAM1_STATE_MESSAGE1), flushed);
  }

  @Nested
  class GlobalState {

    @Test
    void testEmptyQueuesGlobalState() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      // GLOBAL
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE);
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateManager.flushStates());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE));
    }

    @Test
    void testConversion() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var preConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      final var preConvertId2 = simulateIncomingRecords(STREAM3_DESC, 10, stateManager);
      assertEquals(3, Set.of(preConvertId0, preConvertId1, preConvertId2).size());

      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE);

      // Since this is actually a global state, we can only flush after all streams are done.
      stateManager.decrement(preConvertId0, 10);
      assertEquals(List.of(), stateManager.flushStates());
      stateManager.decrement(preConvertId1, 10);
      assertEquals(List.of(), stateManager.flushStates());
      stateManager.decrement(preConvertId2, 10);
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateManager.flushStates());
    }

    @Test
    void testCorrectFlushingOneStream() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE);
      stateManager.decrement(preConvertId0, 10);
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateManager.flushStates());

      final var afterConvertId1 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE);
      stateManager.decrement(afterConvertId1, 10);
      assertEquals(List.of(GLOBAL_STATE_MESSAGE2), stateManager.flushStates());
    }

    @Test
    void testCorrectFlushingManyStreams() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var preConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      assertNotEquals(preConvertId0, preConvertId1);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE);
      stateManager.decrement(preConvertId0, 10);
      stateManager.decrement(preConvertId1, 10);
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateManager.flushStates());

      final var afterConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var afterConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      assertEquals(afterConvertId0, afterConvertId1);
      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE);
      stateManager.decrement(afterConvertId0, 20);
      assertEquals(List.of(GLOBAL_STATE_MESSAGE2), stateManager.flushStates());
    }

  }

  @Nested
  class PerStreamState {

    @Test
    void testEmptyQueues() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      // GLOBAL
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE);
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateManager.flushStates());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE));
    }

    @Test
    void testCorrectFlushingOneStream() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      var stateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE);
      stateManager.decrement(stateId, 3);
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateManager.flushStates());

      stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE);
      stateManager.decrement(stateId, 10);
      assertEquals(List.of(STREAM1_STATE_MESSAGE2), stateManager.flushStates());

    }

    @Test
    void testCorrectFlushingManyStream() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var stream1StateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      final var stream2StateId = simulateIncomingRecords(STREAM2_DESC, 7, stateManager);

      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE);
      stateManager.decrement(stream1StateId, 3);
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateManager.flushStates());

      stateManager.decrement(stream2StateId, 4);
      assertEquals(List.of(), stateManager.flushStates());
      stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE);
      stateManager.decrement(stream2StateId, 3);
      // only flush state if counter is 0.
      assertEquals(List.of(STREAM1_STATE_MESSAGE2), stateManager.flushStates());
    }

  }

  private static long simulateIncomingRecords(final StreamDescriptor desc, final long count, final GlobalAsyncStateManager manager) {
    var stateId = 0L;
    for (int i = 0; i < count; i++) {
      stateId = manager.getStateIdAndIncrementCounter(desc);
    }
    return stateId;
  }

}
