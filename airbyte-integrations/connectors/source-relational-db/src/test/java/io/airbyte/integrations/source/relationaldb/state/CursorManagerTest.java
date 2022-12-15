/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_FIELD2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.CURSOR_RECORD_COUNT;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAME_NAMESPACE_PAIR1;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.NAME_NAMESPACE_PAIR2;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.getCatalog;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.getState;
import static io.airbyte.integrations.source.relationaldb.state.StateTestConstants.getStream;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Collections;
import java.util.Optional;
import java.util.function.Function;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link CursorManager} class.
 */
public class CursorManagerTest {

  private static final Function<DbStreamState, Long> CURSOR_RECORD_COUNT_FUNCTION = stream -> {
    if (stream.getCursorRecordCount() != null) {
      return stream.getCursorRecordCount();
    } else {
      return 0L;
    }
  };

  @Test
  void testCreateCursorInfoCatalogAndStateSameCursorField() {
    final CursorManager<DbStreamState> cursorManager = createCursorManager(CURSOR_FIELD1, CURSOR, NAME_NAMESPACE_PAIR1);
    final CursorInfo actual = cursorManager.createCursorInfoForStream(
        NAME_NAMESPACE_PAIR1,
        getState(CURSOR_FIELD1, CURSOR, CURSOR_RECORD_COUNT),
        getStream(CURSOR_FIELD1),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION);
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, CURSOR_RECORD_COUNT, CURSOR_FIELD1, CURSOR, CURSOR_RECORD_COUNT), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndStateSameCursorFieldButNoCursor() {
    final CursorManager<DbStreamState> cursorManager = createCursorManager(CURSOR_FIELD1, null, NAME_NAMESPACE_PAIR1);
    final CursorInfo actual = cursorManager.createCursorInfoForStream(
        NAME_NAMESPACE_PAIR1,
        getState(CURSOR_FIELD1, null),
        getStream(CURSOR_FIELD1),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION);
    assertEquals(new CursorInfo(CURSOR_FIELD1, null, CURSOR_FIELD1, null), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndStateChangeInCursorFieldName() {
    final CursorManager<DbStreamState> cursorManager = createCursorManager(CURSOR_FIELD1, CURSOR, NAME_NAMESPACE_PAIR1);
    final CursorInfo actual = cursorManager.createCursorInfoForStream(
        NAME_NAMESPACE_PAIR1,
        getState(CURSOR_FIELD1, CURSOR),
        getStream(CURSOR_FIELD2),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION);
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, CURSOR_FIELD2, null), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndNoState() {
    final CursorManager<DbStreamState> cursorManager = createCursorManager(CURSOR_FIELD1, CURSOR, NAME_NAMESPACE_PAIR1);
    final CursorInfo actual = cursorManager.createCursorInfoForStream(
        NAME_NAMESPACE_PAIR1,
        Optional.empty(),
        getStream(CURSOR_FIELD1),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION);
    assertEquals(new CursorInfo(null, null, CURSOR_FIELD1, null), actual);
  }

  @Test
  void testCreateCursorInfoStateAndNoCatalog() {
    final CursorManager<DbStreamState> cursorManager = createCursorManager(CURSOR_FIELD1, CURSOR, NAME_NAMESPACE_PAIR1);
    final CursorInfo actual = cursorManager.createCursorInfoForStream(
        NAME_NAMESPACE_PAIR1,
        getState(CURSOR_FIELD1, CURSOR),
        Optional.empty(),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION);
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, null, null), actual);
  }

  // this is what full refresh looks like.
  @Test
  void testCreateCursorInfoNoCatalogAndNoState() {
    final CursorManager<DbStreamState> cursorManager = createCursorManager(CURSOR_FIELD1, CURSOR, NAME_NAMESPACE_PAIR1);
    final CursorInfo actual = cursorManager.createCursorInfoForStream(
        NAME_NAMESPACE_PAIR1,
        Optional.empty(),
        Optional.empty(),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION);
    assertEquals(new CursorInfo(null, null, null, null), actual);
  }

  @Test
  void testCreateCursorInfoStateAndCatalogButNoCursorField() {
    final CursorManager<DbStreamState> cursorManager = createCursorManager(CURSOR_FIELD1, CURSOR, NAME_NAMESPACE_PAIR1);
    final CursorInfo actual = cursorManager.createCursorInfoForStream(
        NAME_NAMESPACE_PAIR1,
        getState(CURSOR_FIELD1, CURSOR),
        getStream(null),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION);
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, null, null), actual);
  }

  @Test
  void testGetters() {
    final CursorManager cursorManager = createCursorManager(CURSOR_FIELD1, CURSOR, NAME_NAMESPACE_PAIR1);
    final CursorInfo actualCursorInfo = new CursorInfo(CURSOR_FIELD1, CURSOR, null, null);

    assertEquals(Optional.of(actualCursorInfo), cursorManager.getCursorInfo(NAME_NAMESPACE_PAIR1));
    assertEquals(Optional.empty(), cursorManager.getCursorField(NAME_NAMESPACE_PAIR1));
    assertEquals(Optional.empty(), cursorManager.getCursor(NAME_NAMESPACE_PAIR1));

    assertEquals(Optional.empty(), cursorManager.getCursorInfo(NAME_NAMESPACE_PAIR2));
    assertEquals(Optional.empty(), cursorManager.getCursorField(NAME_NAMESPACE_PAIR2));
    assertEquals(Optional.empty(), cursorManager.getCursor(NAME_NAMESPACE_PAIR2));
  }

  private CursorManager<DbStreamState> createCursorManager(final String cursorField,
                                                           final String cursor,
                                                           final AirbyteStreamNameNamespacePair nameNamespacePair) {
    final DbStreamState dbStreamState = getState(cursorField, cursor).get();
    return new CursorManager<>(
        getCatalog(cursorField).orElse(null),
        () -> Collections.singleton(dbStreamState),
        DbStreamState::getCursor,
        DbStreamState::getCursorField,
        CURSOR_RECORD_COUNT_FUNCTION,
        s -> nameNamespacePair);
  }

}
