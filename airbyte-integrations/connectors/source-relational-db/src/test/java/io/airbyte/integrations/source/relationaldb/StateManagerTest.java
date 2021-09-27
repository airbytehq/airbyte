/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.Collections;
import java.util.Comparator;
import java.util.Optional;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.Lists;

class StateManagerTest {

  private static final String NAMESPACE = "public";
  private static final String STREAM_NAME1 = "cars";
  private static final AirbyteStreamNameNamespacePair NAME_NAMESPACE_PAIR1 = new AirbyteStreamNameNamespacePair(STREAM_NAME1, NAMESPACE);
  private static final String STREAM_NAME2 = "bicycles";
  private static final AirbyteStreamNameNamespacePair NAME_NAMESPACE_PAIR2 = new AirbyteStreamNameNamespacePair(STREAM_NAME2, NAMESPACE);
  private static final String STREAM_NAME3 = "stationary_bicycles";
  private static final String CURSOR_FIELD1 = "year";
  private static final String CURSOR_FIELD2 = "generation";
  private static final String CURSOR = "2000";

  @Test
  void testCreateCursorInfoCatalogAndStateSameCursorField() {
    final CursorInfo actual =
        StateManager.createCursorInfoForStream(NAME_NAMESPACE_PAIR1, getState(CURSOR_FIELD1, CURSOR), getCatalog(CURSOR_FIELD1));
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, CURSOR_FIELD1, CURSOR), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndStateSameCursorFieldButNoCursor() {
    final CursorInfo actual =
        StateManager.createCursorInfoForStream(NAME_NAMESPACE_PAIR1, getState(CURSOR_FIELD1, null), getCatalog(CURSOR_FIELD1));
    assertEquals(new CursorInfo(CURSOR_FIELD1, null, CURSOR_FIELD1, null), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndStateChangeInCursorFieldName() {
    final CursorInfo actual =
        StateManager.createCursorInfoForStream(NAME_NAMESPACE_PAIR1, getState(CURSOR_FIELD1, CURSOR), getCatalog(CURSOR_FIELD2));
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, CURSOR_FIELD2, null), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndNoState() {
    final CursorInfo actual = StateManager
        .createCursorInfoForStream(NAME_NAMESPACE_PAIR1, Optional.empty(), getCatalog(CURSOR_FIELD1));
    assertEquals(new CursorInfo(null, null, CURSOR_FIELD1, null), actual);
  }

  @Test
  void testCreateCursorInfoStateAndNoCatalog() {
    final CursorInfo actual = StateManager
        .createCursorInfoForStream(NAME_NAMESPACE_PAIR1, getState(CURSOR_FIELD1, CURSOR), Optional.empty());
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, null, null), actual);
  }

  // this is what full refresh looks like.
  @Test
  void testCreateCursorInfoNoCatalogAndNoState() {
    final CursorInfo actual = StateManager
        .createCursorInfoForStream(NAME_NAMESPACE_PAIR1, Optional.empty(), Optional.empty());
    assertEquals(new CursorInfo(null, null, null, null), actual);
  }

  @Test
  void testCreateCursorInfoStateAndCatalogButNoCursorField() {
    final CursorInfo actual = StateManager
        .createCursorInfoForStream(NAME_NAMESPACE_PAIR1, getState(CURSOR_FIELD1, CURSOR), getCatalog(null));
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, null, null), actual);
  }

  @SuppressWarnings("SameParameterValue")
  private static Optional<DbStreamState> getState(String cursorField, String cursor) {
    return Optional.of(new DbStreamState()
        .withStreamName(STREAM_NAME1)
        .withCursorField(Lists.newArrayList(cursorField))
        .withCursor(cursor));
  }

  private static Optional<ConfiguredAirbyteStream> getCatalog(String cursorField) {
    return Optional.of(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(STREAM_NAME1))
        .withCursorField(cursorField == null ? Collections.emptyList() : Lists.newArrayList(cursorField)));
  }

  @Test
  void testGetters() {
    final DbState state = new DbState().withStreams(Lists.newArrayList(
        new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(Lists.newArrayList(CURSOR_FIELD1))
            .withCursor(CURSOR),
        new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE)));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Lists.newArrayList(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(Lists.newArrayList(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))));

    final StateManager stateManager = new StateManager(state, catalog);

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
        .withStreams(Lists.newArrayList(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(Lists.newArrayList(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))
                .withCursorField(Lists.newArrayList(CURSOR_FIELD2)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME3).withNamespace(NAMESPACE))));

    final StateManager stateManager = new StateManager(new DbState(), catalog);

    final AirbyteStateMessage expectedFirstEmission = new AirbyteStateMessage()
        .withData(Jsons.jsonNode(new DbState().withStreams(Lists
            .newArrayList(
                new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(Lists.newArrayList(CURSOR_FIELD1))
                    .withCursor("a"),
                new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(Lists.newArrayList(CURSOR_FIELD2)),
                new DbStreamState().withStreamName(STREAM_NAME3).withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(false)));
    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);
    final AirbyteStateMessage expectedSecondEmission = new AirbyteStateMessage()
        .withData(Jsons.jsonNode(new DbState().withStreams(Lists
            .newArrayList(
                new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(Lists.newArrayList(CURSOR_FIELD1))
                    .withCursor("a"),
                new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE).withCursorField(Lists.newArrayList(CURSOR_FIELD2))
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
        .withStreams(Lists.newArrayList(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1).withNamespace(NAMESPACE))
                .withCursorField(Lists.newArrayList(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2).withNamespace(NAMESPACE))));
    final StateManager stateManager = new StateManager(new DbState(), catalog);

    final AirbyteStateMessage expectedFirstEmission = new AirbyteStateMessage()
        .withData(Jsons.jsonNode(new DbState().withStreams(Lists
            .newArrayList(
                new DbStreamState().withStreamName(STREAM_NAME1).withStreamNamespace(NAMESPACE).withCursorField(Lists.newArrayList(CURSOR_FIELD1))
                    .withCursor("a"),
                new DbStreamState().withStreamName(STREAM_NAME2).withStreamNamespace(NAMESPACE))
            .stream().sorted(Comparator.comparing(DbStreamState::getStreamName)).collect(Collectors.toList()))
            .withCdc(false)));

    final AirbyteStateMessage actualFirstEmission = stateManager.updateAndEmit(NAME_NAMESPACE_PAIR1, "a");
    assertEquals(expectedFirstEmission, actualFirstEmission);
  }

}
