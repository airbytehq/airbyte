/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cursor_based;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.postgres.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.state.StreamStateManager;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This state manager extends the StreamStateManager to enable writing the state_type and version
 * keys to the stream state when they're going through the iterator Once we have verified that
 * expanding StreamStateManager itself to include this functionality, this class will be removed
 */
public class PostgresCursorBasedStateManager extends StreamStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(StreamStateManager.class);


  public PostgresCursorBasedStateManager(final List<AirbyteStateMessage> airbyteStateMessages, final ConfiguredAirbyteCatalog catalog) {
    super(airbyteStateMessages, catalog);
  }

  @Override
  public AirbyteStateMessage toState(final Optional<AirbyteStreamNameNamespacePair> pair) {
    if (pair.isPresent()) {
      final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfoMap = getPairToCursorInfoMap();
      final Optional<CursorInfo> cursorInfo = Optional.ofNullable(pairToCursorInfoMap.get(pair.get()));

      if (cursorInfo.isPresent()) {
        LOGGER.debug("Generating state message for {}...", pair);
        return new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            // Temporarily include legacy state for backwards compatibility with the platform
            .withData(Jsons.jsonNode(generateDbState(pairToCursorInfoMap)))
            .withStream(generateStreamState(pair.get(), cursorInfo.get()));
      } else {
        LOGGER.warn("Cursor information could not be located in state for stream {}.  Returning a new, empty state message...", pair);
        return new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(new AirbyteStreamState());
      }
    } else {
      LOGGER.warn("Stream not provided.  Returning a new, empty state message...");
      return new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(new AirbyteStreamState());
    }
  }

  /**
   * Generates the stream state for the given stream and cursor information.
   *
   * @param airbyteStreamNameNamespacePair The stream.
   * @param cursorInfo The current cursor.
   * @return The {@link AirbyteStreamState} representing the current state of the stream.
   */
  private AirbyteStreamState generateStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                                 final CursorInfo cursorInfo) {
    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(airbyteStreamNameNamespacePair.getName()).withNamespace(airbyteStreamNameNamespacePair.getNamespace()))
        .withStreamState(Jsons.jsonNode(generateDbStreamState(airbyteStreamNameNamespacePair, cursorInfo)));
  }

  private CursorBasedStatus generateDbStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                               final CursorInfo cursorInfo) {
    final CursorBasedStatus state = new CursorBasedStatus();
    state.setStateType(StateType.CURSOR_BASED);
    state.setVersion(2L);
    state.setStreamName(airbyteStreamNameNamespacePair.getName());
    state.setStreamNamespace(airbyteStreamNameNamespacePair.getNamespace());
    state.setCursorField(cursorInfo.getCursorField() == null ? Collections.emptyList() : Lists.newArrayList(cursorInfo.getCursorField()));
    state.setCursor(cursorInfo.getCursor());
    if (cursorInfo.getCursorRecordCount() > 0L) {
      state.setCursorRecordCount(cursorInfo.getCursorRecordCount());
    }
    return state;
  }

  /**
   * Generates the legacy global state for backwards compatibility.
   *
   * @param pairToCursorInfoMap The map of stream name/namespace tuple to the current cursor
   *        information for that stream
   * @return The legacy {@link DbState}.
   */
  private DbState generateDbState(final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfoMap) {
    return new DbState()
        .withCdc(false)
        .withStreams(pairToCursorInfoMap.entrySet().stream()
            .sorted(Entry.comparingByKey()) // sort by stream name then namespace for sanity.
            .map(e -> generateDbStreamState(e.getKey(), e.getValue()))
            .collect(Collectors.toList()));
  }

}
