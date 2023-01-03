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
import static org.mockito.Mockito.mock;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link LegacyStateManager} class.
 */
public class LegacyStateManagerTest {

  @Test
  void testGetters() {
    final DbState state = new DbState().withStreams(List.of(
        new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
            .withCursor(CURSOR),
        new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE)));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))));

    final StateManager stateManager = new LegacyStateManager(state, catalog);

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
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))
                .withCursorField(List.of(CURSOR_FIELD2)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME3).withNamespace(NAMESPACE))));

    final StateManager stateManager = new LegacyStateManager(new DbState(), catalog);

    final AirbyteStateMessage expectedFirstEmission = new AirbyteStateMessage()
        .withType(AirbyteStateType.LEGACY)
        .withData(Jsons.jsonNode(new DbState().withStreams(List.of(
            new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a"),
            new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD2)),
            new DbStreamState().withStreamName(STREAM_NAME3).withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(false)));
    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);
    final AirbyteStateMessage expectedSecondEmission = new AirbyteStateMessage()
        .withType(AirbyteStateType.LEGACY)
        .withData(Jsons.jsonNode(new DbState().withStreams(List.of(
            new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a"),
            new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD2))
                .withCursor("b"),
            new DbStreamState().withStreamName(STREAM_NAME3).withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(false)));
    final AirbyteStateMessage actualSecondEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR2, "b");
    assertEquals(expectedSecondEmission, actualSecondEmission);
  }

  @Test
  void testToStateNullCursorField() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))));
    final StateManager stateManager = new LegacyStateManager(new DbState(), catalog);

    final AirbyteStateMessage expectedFirstEmission = new AirbyteStateMessage()
        .withType(AirbyteStateType.LEGACY)
        .withData(Jsons.jsonNode(new DbState().withStreams(List.of(
            new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a"),
            new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(false)));

    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);
  }

  @Test
  void testCursorNotUpdatedForCdc() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(List.of(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))));

    final DbState state = new DbState();
    state.setCdc(true);
    final StateManager stateManager = new LegacyStateManager(state, catalog);

    final AirbyteStateMessage expectedFirstEmission = new AirbyteStateMessage()
        .withType(AirbyteStateType.LEGACY)
        .withData(Jsons.jsonNode(new DbState().withStreams(List.of(
            new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
                .withCursor(null),
            new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(List.of()))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(true)));
    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);
    final AirbyteStateMessage expectedSecondEmission = new AirbyteStateMessage()
        .withType(AirbyteStateType.LEGACY)
        .withData(Jsons.jsonNode(new DbState().withStreams(List.of(
            new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(List.of(CURSOR_FIELD1))
                .withCursor(null),
            new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(List.of())
                .withCursor(null))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(true)));
    final AirbyteStateMessage actualSecondEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR2, "b");
    assertEquals(expectedSecondEmission, actualSecondEmission);
  }

  @Test
  void testCdcStateManager() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final CdcState cdcState = new CdcState().withState(Jsons.jsonNode(Map.of("foo", "bar", "baz", 5)));
    final DbState dbState = new DbState().withCdcState(cdcState).withStreams(List.of(
        new DbStreamState().withStreamNamespace(NAMESPACE).withStreamName(STREAM_NAME1)));
    final StateManager stateManager = new LegacyStateManager(dbState, catalog);
    assertNotNull(stateManager.getCdcStateManager());
    assertEquals(cdcState, stateManager.getCdcStateManager().getCdcState());
  }

}
