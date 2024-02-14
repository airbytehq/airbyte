/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.state;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteStateMessage;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteStreamState;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class GlobalAsyncStateManagerTest {

  private static final long TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = 100 * 1024 * 1024; // 10MB
  private static final String DEFAULT_NAMESPACE = "foo_namespace";
  private static final long STATE_MSG_SIZE = 1000;

  private static final String NAMESPACE = "namespace";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = STREAM_NAME + 2;
  private static final String STREAM_NAME3 = STREAM_NAME + 3;
  private static final StreamDescriptor STREAM1_DESC = new StreamDescriptor()
      .withName(STREAM_NAME).withNamespace(NAMESPACE);
  private static final StreamDescriptor STREAM2_DESC = new StreamDescriptor()
      .withName(STREAM_NAME2).withNamespace(NAMESPACE);
  private static final StreamDescriptor STREAM3_DESC = new StreamDescriptor()
      .withName(STREAM_NAME3).withNamespace(NAMESPACE);

  private static final PartialAirbyteMessage GLOBAL_STATE_MESSAGE1 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.GLOBAL));
  private static final PartialAirbyteMessage GLOBAL_STATE_MESSAGE2 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.GLOBAL));
  private static final PartialAirbyteMessage GLOBAL_STATE_MESSAGE3 = new PartialAirbyteMessage()
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

  private static final PartialAirbyteMessage STREAM1_STATE_MESSAGE3 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)));
  private static final PartialAirbyteMessage STREAM2_STATE_MESSAGE = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM2_DESC)));

  @Test
  void testBasic() {
    final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

    final var firstStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC);
    final var secondStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC);
    assertEquals(firstStateId, secondStateId);

    stateManager.decrement(firstStateId, 2);
    // because no state message has been tracked, there is nothing to flush yet.
    final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats =
        stateManager.flushStates().stream()
            .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
    assertEquals(0, stateWithStats.size());

    stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
    final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats2 =
        stateManager.flushStates().stream()
            .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
    assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateWithStats2.keySet().stream().toList());
    assertEquals(List.of(new AirbyteStateStats().withRecordCount(2.0)), stateWithStats2.values().stream().toList());
  }

  @Nested
  class GlobalState {

    @Test
    void testEmptyQueuesGlobalState() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      // GLOBAL
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(0.0)), stateWithStats.values().stream().toList());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE));
    }

    @Test
    void testConversion() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var preConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      final var preConvertId2 = simulateIncomingRecords(STREAM3_DESC, 10, stateManager);
      assertEquals(3, Set.of(preConvertId0, preConvertId1, preConvertId2).size());

      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);

      // Since this is actually a global state, we can only flush after all streams are done.
      stateManager.decrement(preConvertId0, 10);
      assertEquals(List.of(), stateManager.flushStates());
      stateManager.decrement(preConvertId1, 10);
      assertEquals(List.of(), stateManager.flushStates());
      stateManager.decrement(preConvertId2, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(30.0)), stateWithStats.values().stream().toList());

    }

    @Test
    void testCorrectFlushingOneStream() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(preConvertId0, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(10.0)), stateWithStats.values().stream().toList());

      final var afterConvertId1 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(afterConvertId1, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats2 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE2), stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(10.0)), stateWithStats2.values().stream().toList());
    }

    @Test
    void testZeroRecordFlushing() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(preConvertId0, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(10.0)), stateWithStats.values().stream().toList());

      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats2 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE2), stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(0.0)), stateWithStats2.values().stream().toList());

      final var afterConvertId2 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE3, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(afterConvertId2, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats3 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE3), stateWithStats3.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(10.0)), stateWithStats3.values().stream().toList());
    }

    @Test
    void testCorrectFlushingManyStreams() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var preConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      assertNotEquals(preConvertId0, preConvertId1);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(preConvertId0, 10);
      stateManager.decrement(preConvertId1, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(20.0)), stateWithStats.values().stream().toList());

      final var afterConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var afterConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      assertEquals(afterConvertId0, afterConvertId1);
      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(afterConvertId0, 20);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats2 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(GLOBAL_STATE_MESSAGE2), stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(20.0)), stateWithStats2.values().stream().toList());
    }

  }

  @Nested
  class PerStreamState {

    @Test
    void testEmptyQueues() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      // GLOBAL
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(0.0)), stateWithStats.values().stream().toList());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE));
    }

    @Test
    void testCorrectFlushingOneStream() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      var stateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 3);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(3.0)), stateWithStats.values().stream().toList());

      stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats2 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM1_STATE_MESSAGE2), stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(10.0)), stateWithStats2.values().stream().toList());
    }

    @Test
    void testZeroRecordFlushing() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      var stateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 3);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(3.0)), stateWithStats.values().stream().toList());

      stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats2 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM1_STATE_MESSAGE2), stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(0.0)), stateWithStats2.values().stream().toList());

      stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE3, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 10);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats3 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM1_STATE_MESSAGE3), stateWithStats3.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(10.0)), stateWithStats3.values().stream().toList());
    }

    @Test
    void testCorrectFlushingManyStream() {
      final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var stream1StateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      final var stream2StateId = simulateIncomingRecords(STREAM2_DESC, 7, stateManager);

      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stream1StateId, 3);
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM1_STATE_MESSAGE1), stateWithStats.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(3.0)), stateWithStats.values().stream().toList());

      stateManager.decrement(stream2StateId, 4);
      assertEquals(List.of(), stateManager.flushStates());
      stateManager.trackState(STREAM2_STATE_MESSAGE, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stream2StateId, 3);
      // only flush state if counter is 0.
      final Map<PartialAirbyteMessage, AirbyteStateStats> stateWithStats2 = stateManager.flushStates().stream()
          .collect(Collectors.toMap(PartialStateWithDestinationStats::stateMessage, PartialStateWithDestinationStats::stats));
      assertEquals(List.of(STREAM2_STATE_MESSAGE), stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(new AirbyteStateStats().withRecordCount(7.0)), stateWithStats2.values().stream().toList());
    }

  }

  private static long simulateIncomingRecords(final StreamDescriptor desc, final long count, final GlobalAsyncStateManager manager) {
    var stateId = 0L;
    for (int i = 0; i < count; i++) {
      stateId = manager.getStateIdAndIncrementCounter(desc);
    }
    return stateId;
  }

  @Test
  void flushingRecordsShouldNotReduceStatsCounterForGlobalState() {
    final PartialAirbyteMessage globalState = new PartialAirbyteMessage()
        .withState(new PartialAirbyteStateMessage().withType(AirbyteStateType.GLOBAL))
        .withSerialized(Jsons.serialize(ImmutableMap.of("cursor", "1")))
        .withType(Type.STATE);
    final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

    final long stateId = simulateIncomingRecords(STREAM1_DESC, 6, stateManager);
    stateManager.decrement(stateId, 4);
    stateManager.trackState(globalState, 1, STREAM1_DESC.getNamespace());
    final List<PartialStateWithDestinationStats> stateBeforeAllRecordsAreFlushed = stateManager.flushStates();
    assertEquals(0, stateBeforeAllRecordsAreFlushed.size());
    stateManager.decrement(stateId, 2);
    List<PartialStateWithDestinationStats> stateAfterAllRecordsAreFlushed = stateManager.flushStates();
    assertEquals(1, stateAfterAllRecordsAreFlushed.size());
    assertEquals(6.0, stateAfterAllRecordsAreFlushed.get(0).stats().getRecordCount());
  }

}
