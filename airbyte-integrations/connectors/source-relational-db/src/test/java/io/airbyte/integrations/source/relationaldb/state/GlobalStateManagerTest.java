/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAMESPACE;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAME_NAMESPACE_PAIR1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.STREAM_NAME3;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link GlobalStateManager} class.
 */
public class GlobalStateManagerTest {

  @Test
  void testCdcStateManager() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final CdcState cdcState = new CdcState().withState(Jsons.jsonNode(Map.of("foo", "bar", "baz", 5)));
    final AirbyteGlobalState globalState = new AirbyteGlobalState().withSharedState(Jsons.jsonNode(cdcState))
        .withStreamStates(List.of(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withNamespace("namespace").withName("name"))
            .withStreamState(Jsons.jsonNode(new DbStreamState()))));
    final StateManager stateManager =
        new GlobalStateManager(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState), catalog);
    assertNotNull(stateManager.getCdcStateManager());
    assertEquals(cdcState, stateManager.getCdcStateManager().getCdcState());
    assertEquals(1, stateManager.getCdcStateManager().getInitialStreamsSynced().size());
    assertTrue(stateManager.getCdcStateManager().getInitialStreamsSynced().contains(new AirbyteStreamNameNamespacePair("name", "namespace")));
  }

  @Test
  void testToStateFromLegacyState() {
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

    final CdcState cdcState = new CdcState().withState(Jsons.jsonNode(Map.of("foo", "bar", "baz", 5)));
    final DbState dbState = new DbState()
        .withCdc(true)
        .withCdcState(cdcState)
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
    final StateManager stateManager = new GlobalStateManager(new AirbyteStateMessage().withData(Jsons.jsonNode(dbState)), catalog);

    final long expectedRecordCount = 19L;
    final DbState expectedDbState = new DbState()
        .withCdc(true)
        .withCdcState(cdcState)
        .withStreams(List.of(
            new DbStreamState()
                .withStreamName(STREAM_NAME1)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a")
                .withCursorRecordCount(expectedRecordCount),
            new DbStreamState()
                .withStreamName(STREAM_NAME2)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD2)),
            new DbStreamState()
                .withStreamName(STREAM_NAME3)
                .withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()));

    final AirbyteGlobalState expectedGlobalState = new AirbyteGlobalState()
        .withSharedState(Jsons.jsonNode(cdcState))
        .withStreamStates(List.of(
            new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(STREAM_NAME1)
                    .withStreamNamespace(NAMESPACE)
                    .withCursorField(List.of(CURSOR_FIELD1))
                    .withCursor("a")
                    .withCursorRecordCount(expectedRecordCount))),
            new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME2).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(STREAM_NAME2)
                    .withStreamNamespace(NAMESPACE)
                    .withCursorField(List.of(CURSOR_FIELD2)))),
            new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME3).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(STREAM_NAME3)
                    .withStreamNamespace(NAMESPACE))))
            .stream().sorted(Comparator.comparing(o -> o.getStreamDescriptor().getName())).collect(Collectors.toList()));
    final AirbyteStateMessage expected = new AirbyteStateMessage()
        .withData(Jsons.jsonNode(expectedDbState))
        .withGlobal(expectedGlobalState)
        .withType(AirbyteStateType.GLOBAL);

    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a", expectedRecordCount);
    assertEquals(expected, actualFirstEmission);
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

    final CdcState cdcState = new CdcState().withState(Jsons.jsonNode(Map.of("foo", "bar", "baz", 5)));
    final AirbyteGlobalState globalState = new AirbyteGlobalState().withSharedState(Jsons.jsonNode(new DbState())).withStreamStates(
        List.of(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor()).withStreamState(Jsons.jsonNode(new DbStreamState()))));
    final StateManager stateManager =
        new GlobalStateManager(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState), catalog);
    stateManager.getCdcStateManager().setCdcState(cdcState);

    final DbState expectedDbState = new DbState()
        .withCdc(true)
        .withCdcState(cdcState)
        .withStreams(List.of(
            new DbStreamState()
                .withStreamName(STREAM_NAME1)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD1))
                .withCursor("a")
                .withCursorRecordCount(1L),
            new DbStreamState()
                .withStreamName(STREAM_NAME2)
                .withStreamNamespace(NAMESPACE)
                .withCursorField(List.of(CURSOR_FIELD2)),
            new DbStreamState()
                .withStreamName(STREAM_NAME3)
                .withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()));

    final AirbyteGlobalState expectedGlobalState = new AirbyteGlobalState()
        .withSharedState(Jsons.jsonNode(cdcState))
        .withStreamStates(List.of(
            new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(STREAM_NAME1)
                    .withStreamNamespace(NAMESPACE)
                    .withCursorField(List.of(CURSOR_FIELD1))
                    .withCursor("a")
                    .withCursorRecordCount(1L))),
            new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME2).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(STREAM_NAME2)
                    .withStreamNamespace(NAMESPACE)
                    .withCursorField(List.of(CURSOR_FIELD2)))),
            new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME3).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(STREAM_NAME3)
                    .withStreamNamespace(NAMESPACE))))
            .stream().sorted(Comparator.comparing(o -> o.getStreamDescriptor().getName())).collect(Collectors.toList()));
    final AirbyteStateMessage expected = new AirbyteStateMessage()
        .withData(Jsons.jsonNode(expectedDbState))
        .withGlobal(expectedGlobalState)
        .withType(AirbyteStateType.GLOBAL);

    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a", 1L);
    assertEquals(expected, actualFirstEmission);
  }

  @Test
  void testToStateWithNoState() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog();
    final StateManager stateManager =
        new GlobalStateManager(new AirbyteStateMessage(), catalog);

    final AirbyteStateMessage airbyteStateMessage = stateManager.toState(Optional.empty());
    assertNotNull(airbyteStateMessage);
    assertEquals(AirbyteStateType.GLOBAL, airbyteStateMessage.getType());
    assertEquals(0, airbyteStateMessage.getGlobal().getStreamStates().size());
  }

  @Test
  void testCdcStateManagerLegacyState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final CdcState cdcState = new CdcState().withState(Jsons.jsonNode(Map.of("foo", "bar", "baz", 5)));
    final DbState dbState = new DbState().withCdcState(new CdcState().withState(Jsons.jsonNode(cdcState)))
        .withStreams(List
            .of(new DbStreamState().withStreamName("name").withStreamNamespace("namespace").withCursor("").withCursorField(Collections.emptyList())))
        .withCdc(true);
    final StateManager stateManager =
        new GlobalStateManager(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY).withData(Jsons.jsonNode(dbState)), catalog);
    assertNotNull(stateManager.getCdcStateManager());
    assertEquals(1, stateManager.getCdcStateManager().getInitialStreamsSynced().size());
    assertTrue(stateManager.getCdcStateManager().getInitialStreamsSynced().contains(new AirbyteStreamNameNamespacePair("name", "namespace")));
  }

}
