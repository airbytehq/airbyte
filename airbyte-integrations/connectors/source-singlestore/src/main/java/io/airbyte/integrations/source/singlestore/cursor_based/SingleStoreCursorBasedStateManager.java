/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore.cursor_based;

import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.StreamStateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.singlestore.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.singlestore.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreCursorBasedStateManager extends StreamStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreCursorBasedStateManager.class);

  public SingleStoreCursorBasedStateManager(final List<AirbyteStateMessage> airbyteStateMessages, final ConfiguredAirbyteCatalog catalog) {
    super(airbyteStateMessages, catalog);
  }

  @Override
  public AirbyteStateMessage toState(@NotNull final Optional<AirbyteStreamNameNamespacePair> pair) {
    if (pair.isPresent()) {
      final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfoMap = getPairToCursorInfoMap();
      final Optional<CursorInfo> cursorInfo = Optional.ofNullable(pairToCursorInfoMap.get(pair.get()));

      if (cursorInfo.isPresent()) {
        LOGGER.debug("Generating state message for {}...", pair);
        return new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
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
  private static AirbyteStreamState generateStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                                        final CursorInfo cursorInfo) {
    return new AirbyteStreamState().withStreamDescriptor(
        new StreamDescriptor().withName(airbyteStreamNameNamespacePair.getName()).withNamespace(airbyteStreamNameNamespacePair.getNamespace()))
        .withStreamState(Jsons.jsonNode(generateDbStreamState(airbyteStreamNameNamespacePair, cursorInfo)));
  }

  private static CursorBasedStatus generateDbStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                                         final CursorInfo cursorInfo) {
    final CursorBasedStatus state = new CursorBasedStatus();
    state.setStateType(StateType.CURSOR_BASED);
    state.setStreamName(airbyteStreamNameNamespacePair.getName());
    state.setStreamNamespace(airbyteStreamNameNamespacePair.getNamespace());
    state.setCursorField(cursorInfo.getCursorField() == null ? Collections.emptyList() : Lists.newArrayList(cursorInfo.getCursorField()));
    state.setCursor(cursorInfo.getCursor());
    if (cursorInfo.getCursorRecordCount() > 0L) {
      state.setCursorRecordCount(cursorInfo.getCursorRecordCount());
    }
    return state;
  }

}
