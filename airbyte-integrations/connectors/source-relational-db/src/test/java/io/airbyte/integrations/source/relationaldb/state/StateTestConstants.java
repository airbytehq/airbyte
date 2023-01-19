/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.testcontainers.shaded.com.google.common.collect.Lists;

/**
 * Collection of constants for use in state management-related tests.
 */
public final class StateTestConstants {

  public static final String NAMESPACE = "public";
  public static final String STREAM_NAME1 = "cars";
  public static final AirbyteStreamNameNamespacePair NAME_NAMESPACE_PAIR1 = new AirbyteStreamNameNamespacePair(STREAM_NAME1, NAMESPACE);
  public static final String STREAM_NAME2 = "bicycles";
  public static final AirbyteStreamNameNamespacePair NAME_NAMESPACE_PAIR2 = new AirbyteStreamNameNamespacePair(STREAM_NAME2, NAMESPACE);
  public static final String STREAM_NAME3 = "stationary_bicycles";
  public static final String CURSOR_FIELD1 = "year";
  public static final String CURSOR_FIELD2 = "generation";
  public static final String CURSOR = "2000";
  public static final long CURSOR_RECORD_COUNT = 19L;

  private StateTestConstants() {}

  public static Optional<DbStreamState> getState(final String cursorField, final String cursor) {
    return Optional.of(new DbStreamState()
        .withStreamName(STREAM_NAME1)
        .withCursorField(Lists.newArrayList(cursorField))
        .withCursor(cursor));
  }

  public static Optional<DbStreamState> getState(final String cursorField, final String cursor, final long cursorRecordCount) {
    return Optional.of(new DbStreamState()
        .withStreamName(STREAM_NAME1)
        .withCursorField(Lists.newArrayList(cursorField))
        .withCursor(cursor)
        .withCursorRecordCount(cursorRecordCount));
  }

  public static Optional<ConfiguredAirbyteCatalog> getCatalog(final String cursorField) {
    return Optional.of(new ConfiguredAirbyteCatalog()
        .withStreams(List.of(getStream(cursorField).orElse(null))));
  }

  public static Optional<ConfiguredAirbyteStream> getStream(final String cursorField) {
    return Optional.of(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(STREAM_NAME1))
        .withCursorField(cursorField == null ? Collections.emptyList() : Lists.newArrayList(cursorField)));
  }

}
