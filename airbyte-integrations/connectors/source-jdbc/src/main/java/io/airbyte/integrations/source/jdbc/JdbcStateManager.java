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

import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.integrations.source.jdbc.models.JdbcStreamState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Handles the state machine for the state of jdbc source implementations.
 */
public class JdbcStateManager {

  private final Map<String, CursorInfo> map;

  public JdbcStateManager(JdbcState serialized) {
    map = serialized.getStreams()
        .stream()
        .peek(s -> {
          Preconditions.checkState(s.getCursorField().size() != 0, "No cursor field specified for stream attempting to do incremental.");
          Preconditions.checkState(s.getCursorField().size() == 1, "JdbcSource does not support composite cursor fields.");
        })
        .collect(Collectors.toMap(JdbcStreamState::getStreamName, s -> new CursorInfo(s.getCursorField().get(0), s.getCursor())));
  }

  private Optional<CursorInfo> getCursorInfo(String streamName) {
    return Optional.ofNullable(map.get(streamName));
  }

  public Optional<String> getOriginalCursorField(String streamName) {
    return getCursorInfo(streamName).map(CursorInfo::getOriginalCursorField);
  }

  public Optional<String> getOriginalCursor(String streamName) {
    return getCursorInfo(streamName).map(CursorInfo::getOriginalCursor);
  }

  public Optional<String> getCursorField(String streamName) {
    return getCursorInfo(streamName).map(CursorInfo::getCursor);
  }

  public Optional<String> getCursor(String streamName) {
    return getCursorInfo(streamName).map(CursorInfo::getCursor);
  }

  synchronized public AirbyteStateMessage updateAndEmit(String streamName, String cursorField, String cursor) {
    final Optional<CursorInfo> cursorInfo = getCursorInfo(streamName);

    if (cursorInfo.isPresent()) {
      if (!cursorInfo.get().getCursorField().equals(cursorField)) {
        cursorInfo.get().setCursorField(cursorField);
      }
      cursorInfo.get().setCursor(cursor);
    } else {
      map.put(streamName, new CursorInfo(null, null)
          .setCursorField(cursorField)
          .setCursor(cursor));
    }

    return toState();
  }

  private AirbyteStateMessage toState() {
    final JdbcState jdbcState = new JdbcState()
        .withStreams(map.entrySet().stream()
            .map(e -> new JdbcStreamState()
                .withStreamName(e.getKey())
                .withCursorField(Lists.newArrayList(e.getValue().getCursorField()))
                .withCursor(e.getValue().cursor))
            .collect(Collectors.toList()));

    return new AirbyteStateMessage().withData(Jsons.jsonNode(jdbcState));
  }

  private static class CursorInfo {

    private final String originalCursorField;
    private final String originalCursor;

    private String cursorField;
    private String cursor;

    public CursorInfo(String cursorField, String cursor) {
      this.originalCursorField = cursorField;
      this.originalCursor = cursor;
      this.cursorField = cursorField;
      this.cursor = cursor;
    }

    public String getOriginalCursorField() {
      return originalCursorField;
    }

    public String getOriginalCursor() {
      return originalCursor;
    }

    public String getCursorField() {
      return cursorField;
    }

    public String getCursor() {
      return cursor;
    }

    public CursorInfo setCursorField(String cursorField) {
      this.cursorField = cursorField;
      return this;
    }

    public CursorInfo setCursor(String cursor) {
      this.cursor = cursor;
      return this;
    }

  }

}
