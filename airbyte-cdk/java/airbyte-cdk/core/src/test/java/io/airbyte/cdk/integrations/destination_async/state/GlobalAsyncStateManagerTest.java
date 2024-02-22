/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.state;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteStateMessage;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteStreamState;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.util.*;
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
          .withType(AirbyteStateType.GLOBAL))
      .withSerialized(serializedState(STREAM1_DESC, AirbyteStateType.GLOBAL, Jsons.jsonNode(ImmutableMap.of("cursor", 1))));
  private static final PartialAirbyteMessage GLOBAL_STATE_MESSAGE2 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.GLOBAL))
      .withSerialized(serializedState(STREAM2_DESC, AirbyteStateType.GLOBAL, Jsons.jsonNode(ImmutableMap.of("cursor", 2))));

  private static final PartialAirbyteMessage GLOBAL_STATE_MESSAGE3 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.GLOBAL))
      .withSerialized(serializedState(STREAM3_DESC, AirbyteStateType.GLOBAL, Jsons.jsonNode(ImmutableMap.of("cursor", 2))));
  private static final PartialAirbyteMessage STREAM1_STATE_MESSAGE1 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)))
      .withSerialized(serializedState(STREAM1_DESC, AirbyteStateType.STREAM, Jsons.jsonNode(ImmutableMap.of("cursor", 1))));
  private static final PartialAirbyteMessage STREAM1_STATE_MESSAGE2 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)))
      .withSerialized(serializedState(STREAM1_DESC, AirbyteStateType.STREAM, Jsons.jsonNode(ImmutableMap.of("cursor", 2))));

  private static final PartialAirbyteMessage STREAM1_STATE_MESSAGE3 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM1_DESC)))
      .withSerialized(serializedState(STREAM1_DESC, AirbyteStateType.STREAM, Jsons.jsonNode(ImmutableMap.of("cursor", 3))));
  private static final PartialAirbyteMessage STREAM2_STATE_MESSAGE = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new PartialAirbyteStreamState().withStreamDescriptor(STREAM2_DESC)))
      .withSerialized(serializedState(STREAM2_DESC, AirbyteStateType.STREAM, Jsons.jsonNode(ImmutableMap.of("cursor", 4))));

  public static String serializedState(final StreamDescriptor streamDescriptor, final AirbyteStateType type, final JsonNode state) {
    switch (type) {
      case GLOBAL -> {
        return Jsons.serialize(new AirbyteMessage().withType(Type.STATE).withState(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.GLOBAL)
                .withGlobal(new AirbyteGlobalState()
                    .withSharedState(state)
                    .withStreamStates(Collections.singletonList(new AirbyteStreamState()
                        .withStreamState(Jsons.emptyObject())
                        .withStreamDescriptor(streamDescriptor))))));

      }
      case STREAM -> {
        return Jsons.serialize(new AirbyteMessage().withType(Type.STATE).withState(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamState(state)
                    .withStreamDescriptor(streamDescriptor))));
      }
      default -> throw new RuntimeException("LEGACY STATE NOT SUPPORTED");
    }
  }

  @Test
  void testBasic() {
    final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
    final GlobalAsyncStateManager stateManager =
        new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

    final var firstStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC);
    final var secondStateId = stateManager.getStateIdAndIncrementCounter(STREAM1_DESC);
    assertEquals(firstStateId, secondStateId);

    stateManager.decrement(firstStateId, 2);
    stateManager.flushStates(emittedStatesFromDestination::add);
    // because no state message has been tracked, there is nothing to flush yet.
    final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
        emittedStatesFromDestination.stream()
            .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
    assertEquals(0, stateWithStats.size());

    stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
    stateManager.flushStates(emittedStatesFromDestination::add);

    final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(2.0);
    final Map<AirbyteMessage, AirbyteStateStats> stateWithStats2 =
        emittedStatesFromDestination.stream()
            .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
    assertEquals(
        List.of(
            attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
        stateWithStats2.keySet().stream().toList());
    assertEquals(List.of(expectedDestinationStats), stateWithStats2.values().stream().toList());
  }

  public AirbyteMessage attachDestinationStateStats(final AirbyteMessage stateMessage, final AirbyteStateStats airbyteStateStats) {
    stateMessage.getState().withDestinationStats(airbyteStateStats);
    return stateMessage;
  }

  @Nested
  class GlobalState {

    @Test
    void testEmptyQueuesGlobalState() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      // GLOBAL
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(0.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      //
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE));
    }

    @Test
    void testConversion() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var preConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      final var preConvertId2 = simulateIncomingRecords(STREAM3_DESC, 10, stateManager);
      assertEquals(3, Set.of(preConvertId0, preConvertId1, preConvertId2).size());

      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);

      // Since this is actually a global state, we can only flush after all streams are done.
      stateManager.decrement(preConvertId0, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      assertEquals(0, emittedStatesFromDestination.size());
      stateManager.decrement(preConvertId1, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      assertEquals(0, emittedStatesFromDestination.size());
      stateManager.decrement(preConvertId2, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(30.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());

    }

    @Test
    void testCorrectFlushingOneStream() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(preConvertId0, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(10.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());

      emittedStatesFromDestination.clear();

      final var afterConvertId1 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(afterConvertId1, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats2 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE2.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats2.values().stream().toList());
    }

    @Test
    void testZeroRecordFlushing() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(preConvertId0, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(10.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());
      emittedStatesFromDestination.clear();

      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats2 = new AirbyteStateStats().withRecordCount(0.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats2 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE2.getSerialized(), AirbyteMessage.class), expectedDestinationStats2)),
          stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats2), stateWithStats2.values().stream().toList());
      emittedStatesFromDestination.clear();

      final var afterConvertId2 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(GLOBAL_STATE_MESSAGE3, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(afterConvertId2, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats3 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE3.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats3.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats3.values().stream().toList());
    }

    @Test
    void testCorrectFlushingManyStreams() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var preConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var preConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      assertNotEquals(preConvertId0, preConvertId1);
      stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(preConvertId0, 10);
      stateManager.decrement(preConvertId1, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(20.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());
      emittedStatesFromDestination.clear();

      final var afterConvertId0 = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      final var afterConvertId1 = simulateIncomingRecords(STREAM2_DESC, 10, stateManager);
      assertEquals(afterConvertId0, afterConvertId1);
      stateManager.trackState(GLOBAL_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(afterConvertId0, 20);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats2 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(GLOBAL_STATE_MESSAGE2.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats2.values().stream().toList());
    }

  }

  @Nested
  class PerStreamState {

    @Test
    void testEmptyQueues() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      // GLOBAL
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(0.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());

      assertThrows(IllegalArgumentException.class, () -> stateManager.trackState(GLOBAL_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE));
    }

    @Test
    void testCorrectFlushingOneStream() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      var stateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 3);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(3.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());

      emittedStatesFromDestination.clear();

      stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats2 = new AirbyteStateStats().withRecordCount(10.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats2 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(List.of(
          attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE2.getSerialized(), AirbyteMessage.class), expectedDestinationStats2)),
          stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats2), stateWithStats2.values().stream().toList());
    }

    @Test
    void testZeroRecordFlushing() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      var stateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 3);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(3.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());
      emittedStatesFromDestination.clear();

      stateManager.trackState(STREAM1_STATE_MESSAGE2, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats2 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      final AirbyteStateStats expectedDestinationStats2 = new AirbyteStateStats().withRecordCount(0.0);
      assertEquals(List.of(
          attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE2.getSerialized(), AirbyteMessage.class), expectedDestinationStats2)),
          stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats2), stateWithStats2.values().stream().toList());
      emittedStatesFromDestination.clear();

      stateId = simulateIncomingRecords(STREAM1_DESC, 10, stateManager);
      stateManager.trackState(STREAM1_STATE_MESSAGE3, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stateId, 10);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats3 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      final AirbyteStateStats expectedDestinationStats3 = new AirbyteStateStats().withRecordCount(10.0);
      assertEquals(List.of(
          attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE3.getSerialized(), AirbyteMessage.class), expectedDestinationStats3)),
          stateWithStats3.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats3), stateWithStats3.values().stream().toList());
    }

    @Test
    void testCorrectFlushingManyStream() {
      final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
      final GlobalAsyncStateManager stateManager =
          new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));

      final var stream1StateId = simulateIncomingRecords(STREAM1_DESC, 3, stateManager);
      final var stream2StateId = simulateIncomingRecords(STREAM2_DESC, 7, stateManager);

      stateManager.trackState(STREAM1_STATE_MESSAGE1, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stream1StateId, 3);
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats = new AirbyteStateStats().withRecordCount(3.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(STREAM1_STATE_MESSAGE1.getSerialized(), AirbyteMessage.class), expectedDestinationStats)),
          stateWithStats.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats), stateWithStats.values().stream().toList());
      emittedStatesFromDestination.clear();

      stateManager.decrement(stream2StateId, 4);
      stateManager.flushStates(emittedStatesFromDestination::add);
      assertEquals(List.of(), emittedStatesFromDestination);
      stateManager.trackState(STREAM2_STATE_MESSAGE, STATE_MSG_SIZE, DEFAULT_NAMESPACE);
      stateManager.decrement(stream2StateId, 3);
      // only flush state if counter is 0.
      stateManager.flushStates(emittedStatesFromDestination::add);
      final AirbyteStateStats expectedDestinationStats2 = new AirbyteStateStats().withRecordCount(7.0);
      final Map<AirbyteMessage, AirbyteStateStats> stateWithStats2 =
          emittedStatesFromDestination.stream()
              .collect(Collectors.toMap(c -> c, c -> c.getState().getDestinationStats()));
      assertEquals(
          List.of(
              attachDestinationStateStats(Jsons.deserialize(STREAM2_STATE_MESSAGE.getSerialized(), AirbyteMessage.class), expectedDestinationStats2)),
          stateWithStats2.keySet().stream().toList());
      assertEquals(List.of(expectedDestinationStats2), stateWithStats2.values().stream().toList());
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
    final List<AirbyteMessage> emittedStatesFromDestination = new ArrayList<>();
    final GlobalAsyncStateManager stateManager =
        new GlobalAsyncStateManager(new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));
    final long stateId = simulateIncomingRecords(STREAM1_DESC, 6, stateManager);
    stateManager.decrement(stateId, 4);
    stateManager.trackState(GLOBAL_STATE_MESSAGE1, 1, STREAM1_DESC.getNamespace());
    stateManager.flushStates(emittedStatesFromDestination::add);
    assertEquals(0, emittedStatesFromDestination.size());
    stateManager.decrement(stateId, 2);
    stateManager.flushStates(emittedStatesFromDestination::add);
    assertEquals(1, emittedStatesFromDestination.size());
    assertEquals(6.0, emittedStatesFromDestination.getFirst().getState().getDestinationStats().getRecordCount());
  }

}
