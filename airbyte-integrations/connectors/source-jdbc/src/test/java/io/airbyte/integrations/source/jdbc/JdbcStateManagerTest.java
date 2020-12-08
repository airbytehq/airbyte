/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.source.jdbc.JdbcStateManager.CursorInfo;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.integrations.source.jdbc.models.JdbcStreamState;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.Lists;

class JdbcStateManagerTest {

  private static final String STREAM_NAME1 = "cars";
  private static final String STREAM_NAME2 = "bicycles";
  private static final String CURSOR_FIELD1 = "year";
  private static final String CURSOR_FIELD2 = "generation";
  private static final String CURSOR = "2000";

  @Test
  void testCreateCursorInfoCatalogAndStateSameCursorField() {
    final CursorInfo actual = JdbcStateManager.createCursorInfoForStream(STREAM_NAME1, getState(CURSOR_FIELD1, CURSOR), getCatalog(CURSOR_FIELD1));
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, CURSOR_FIELD1, CURSOR), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndStateSameCursorFieldButNoCursor() {
    final CursorInfo actual = JdbcStateManager.createCursorInfoForStream(STREAM_NAME1, getState(CURSOR_FIELD1, null), getCatalog(CURSOR_FIELD1));
    assertEquals(new CursorInfo(CURSOR_FIELD1, null, CURSOR_FIELD1, null), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndStateChangeInCursorFieldName() {
    final CursorInfo actual = JdbcStateManager.createCursorInfoForStream(STREAM_NAME1, getState(CURSOR_FIELD1, CURSOR), getCatalog(CURSOR_FIELD2));
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, CURSOR_FIELD2, null), actual);
  }

  @Test
  void testCreateCursorInfoCatalogAndNoState() {
    final CursorInfo actual = JdbcStateManager.createCursorInfoForStream(STREAM_NAME1, Optional.empty(), getCatalog(CURSOR_FIELD1));
    assertEquals(new CursorInfo(null, null, CURSOR_FIELD1, null), actual);
  }

  @Test
  void testCreateCursorInfoStateAndNoCatalog() {
    final CursorInfo actual = JdbcStateManager.createCursorInfoForStream(STREAM_NAME1, getState(CURSOR_FIELD1, CURSOR), Optional.empty());
    assertEquals(new CursorInfo(CURSOR_FIELD1, CURSOR, null, null), actual);
  }

  // maybe this happens on full refreshes?
  // this should never happen, but for completeness, making sure manager handles all possible logical
  // cases gracefully.
  @Test
  void testCreateCursorInfoNoCatalogAndNoState() {
    final CursorInfo actual = JdbcStateManager.createCursorInfoForStream(STREAM_NAME1, Optional.empty(), Optional.empty());
    assertEquals(new CursorInfo(null, null, null, null), actual);
  }

  @SuppressWarnings("SameParameterValue")
  private static Optional<JdbcStreamState> getState(String cursorField, String cursor) {
    return Optional.of(new JdbcStreamState()
        .withStreamName(STREAM_NAME1)
        .withCursorField(Lists.newArrayList(cursorField))
        .withCursor(cursor));
  }

  private static Optional<ConfiguredAirbyteStream> getCatalog(String cursorField) {
    return Optional.of(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(STREAM_NAME1))
        .withCursorField(Lists.newArrayList(cursorField)));
  }

  @Test
  void test() {
    final JdbcState state = new JdbcState().withStreams(Lists.newArrayList(
        new JdbcStreamState().withStreamName(STREAM_NAME1).withCursorField(Lists.newArrayList(CURSOR_FIELD1)).withCursor(CURSOR),
        new JdbcStreamState().withStreamName(STREAM_NAME2)));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Lists.newArrayList(
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME1))
                .withCursorField(Lists.newArrayList(CURSOR_FIELD1)),
            new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(STREAM_NAME2))));

    final JdbcStateManager stateManager = new JdbcStateManager(state, catalog);

    assertEquals(Optional.of(CURSOR_FIELD1), stateManager.getOriginalCursorField(STREAM_NAME1));
    assertEquals(Optional.of(CURSOR), stateManager.getOriginalCursor(STREAM_NAME1));
    assertEquals(Optional.of(CURSOR_FIELD1), stateManager.getCursorField(STREAM_NAME1));
    assertEquals(Optional.of(CURSOR), stateManager.getCursor(STREAM_NAME1));

    assertEquals(Optional.empty(), stateManager.getOriginalCursorField(STREAM_NAME2));
    assertEquals(Optional.empty(), stateManager.getOriginalCursor(STREAM_NAME2));
    assertEquals(Optional.empty(), stateManager.getCursorField(STREAM_NAME2));
    assertEquals(Optional.empty(), stateManager.getCursor(STREAM_NAME2));
  }

}
