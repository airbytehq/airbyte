/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAMESPACE;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAME_NAMESPACE_PAIR1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAME_NAMESPACE_PAIR2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME3;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.mock;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link StreamStateManager} class.
 */
public class StreamStateManagerTest {

  @Test
  void testCreationFromInvalidState() {
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState()
            .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME1).withNamespace(NAMESPACE))
            .withStreamState(Jsons.jsonNode("Not a state object")));
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);

    Assertions.assertDoesNotThrow(() -> {
      final StateManager stateManager = new StreamStateManager(List.of(airbyteStateMessage), catalog);
      assertNotNull(stateManager);
    });
  }

  @Test
  void testGetters() {
    final List<AirbyteStateMessage> state = new ArrayList<>();
    state.add(createStreamState(STREAM_NAME1, NAMESPACE, List.of(CURSOR_FIELD1), CURSOR, 0L));
    state.add(createStreamState(STREAM_NAME2, NAMESPACE, List.of(), null, 0L));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))));

    final StateManager stateManager = new StreamStateManager(state, catalog);

    assertEquals(Optional.of(CURSOR_FIELD1), stateManager.getOriginalCursorField(NAME_NAMESPACE_PAIR1));
    assertEquals(Optional.of(CURSOR), stateManager.getOriginalCursor(NAME_NAMESPACE_PAIR1));
    assertEquals(Optional.of(CURSOR_FIELD1), stateManager.getCursorField(NAME_NAMESPACE_PAIR1));
    assertEquals(Optional.of(CURSOR), stateManager.getCursor(NAME_NAMESPACE_PAIR1));

    assertEquals(Optional.empty(), stateManager.getOriginalCursorField(NAME_NAMESPACE_PAIR2));
    assertEquals(Optional.empty(), stateManager.getOriginalCursor(NAME_NAMESPACE_PAIR2));
    assertEquals(Optional.empty(), stateManager.getCursorField(NAME_NAMESPACE_PAIR2));
    assertEquals(Optional.empty(), stateManager.getCursor(NAME_NAMESPACE_PAIR2));
  }

  @Test
  void testToState() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD2)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME3).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))));

    final StateManager stateManager = new StreamStateManager(createDefaultState(), catalog);

    final DbState expectedFirstDbState = new DbState()
        .withCdc(false)
        .withStreams(List.of(
            new DbStreamState()
                .withStreamName(STREAM_NAME1)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a"),
            new DbStreamState()
                .withStreamName(STREAM_NAME2)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD2)),
            new DbStreamState()
                .withStreamName(STREAM_NAME3)
                .withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()));
    final AirbyteStateMessage expectedFirstEmission =
        createStreamState(STREAM_NAME1, NAMESPACE, List.of(CURSOR_FIELD1), "a", 0L).withData(Jsons.jsonNode(expectedFirstDbState));

    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);

    final long expectedRecordCount = 17L;
    final DbState expectedSecondDbState = new DbState()
        .withCdc(false)
        .withStreams(List.of(
            new DbStreamState()
                .withStreamName(STREAM_NAME1)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a"),
            new DbStreamState()
                .withStreamName(STREAM_NAME2)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD2))
                .withCursor("b")
                .withCursorRecordCount(expectedRecordCount),
            new DbStreamState()
                .withStreamName(STREAM_NAME3)
                .withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()));
    final AirbyteStateMessage expectedSecondEmission =
        createStreamState(STREAM_NAME2, NAMESPACE, List.of(CURSOR_FIELD2), "b", expectedRecordCount).withData(Jsons.jsonNode(expectedSecondDbState));

    final AirbyteStateMessage actualSecondEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR2, "b", expectedRecordCount);
    assertEquals(expectedSecondEmission, actualSecondEmission);
  }

  @Test
  void testToStateWithoutCursorInfo() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD2)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME3).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))));
    final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair = new AirbyteStreamNameNamespacePair("other", "other");

    final StateManager stateManager = new StreamStateManager(createDefaultState(), catalog);
    final AirbyteStateMessage airbyteStateMessage = stateManager.toState(Optional.of(airbyteStreamNameNamespacePair));
    assertNotNull(airbyteStateMessage);
    assertEquals(AirbyteStateType.STREAM, airbyteStateMessage.getType());
    assertNotNull(airbyteStateMessage.getStream());
  }

  @Test
  void testToStateWithoutStreamPair() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD2)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME3).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))));

    final StateManager stateManager = new StreamStateManager(createDefaultState(), catalog);
    final AirbyteStateMessage airbyteStateMessage = stateManager.toState(Optional.empty());
    assertNotNull(airbyteStateMessage);
    assertEquals(AirbyteStateType.STREAM, airbyteStateMessage.getType());
    assertNotNull(airbyteStateMessage.getStream());
    assertNull(airbyteStateMessage.getStream().getStreamState());
  }

  @Test
  void testToStateNullCursorField() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE)
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))));
    final StateManager stateManager = new StreamStateManager(createDefaultState(), catalog);

    final DbState expectedFirstDbState = new DbState()
        .withCdc(false)
        .withStreams(List.of(
            new DbStreamState()
                .withStreamName(STREAM_NAME1)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a"),
            new DbStreamState()
                .withStreamName(STREAM_NAME2)
                .withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()));

    final AirbyteStateMessage expectedFirstEmission =
        createStreamState(STREAM_NAME1, NAMESPACE, List.of(CURSOR_FIELD1), "a", 0L).withData(Jsons.jsonNode(expectedFirstDbState));
    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);
  }

  @Test
  void testCdcStateManager() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final StateManager stateManager = new StreamStateManager(
        List.of(new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(new AirbyteStreamState())), catalog);
    Assertions.assertThrows(UnsupportedOperationException.class, () -> stateManager.getCdcStateManager());
  }

  private List<AirbyteStateMessage> createDefaultState() {
    return List.of(new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(new AirbyteStreamState()));
  }

  private AirbyteStateMessage createStreamState(final String name,
                                                final String namespace,
                                                final List<String> cursorFields,
                                                final String cursorValue,
                                                final long cursorRecordCount) {
    final DbStreamState dbStreamState = new DbStreamState()
        .withStreamName(name)
        .withStreamNamespace(namespace);

    if (cursorFields != null && !cursorFields.isEmpty()) {
      dbStreamState.withCursorField(cursorFields);
    }

    if (cursorValue != null) {
      dbStreamState.withCursor(cursorValue);
    }

    if (cursorRecordCount > 0L) {
      dbStreamState.withCursorRecordCount(cursorRecordCount);
    }

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState()
            .withStreamDescriptor(new StreamDescriptor().withName(name).withNamespace(namespace))
            .withStreamState(Jsons.jsonNode(dbStreamState)));
  }

}
