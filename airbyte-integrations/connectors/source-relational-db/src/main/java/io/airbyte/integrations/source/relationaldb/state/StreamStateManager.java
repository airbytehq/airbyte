/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_FIELD_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.CURSOR_RECORD_COUNT_FUNCTION;
import static io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils.NAME_NAMESPACE_PAIR_FUNCTION;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Per-stream implementation of the {@link StateManager} interface.
 * <p/>
 * This implementation generates a state object for each stream detected in catalog/map of known
 * streams to cursor information stored in this manager.
 */
public class StreamStateManager extends AbstractStateManager<AirbyteStateMessage, AirbyteStreamState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(StreamStateManager.class);

  /**
   * Constructs a new {@link StreamStateManager} that is seeded with the provided
   * {@link AirbyteStateMessage}.
   *
   * @param airbyteStateMessages The initial state represented as a list of
   *        {@link AirbyteStateMessage}s.
   * @param catalog The {@link ConfiguredAirbyteCatalog} for the connector associated with this state
   *        manager.
   */
  public StreamStateManager(final List<AirbyteStateMessage> airbyteStateMessages, final ConfiguredAirbyteCatalog catalog) {
    super(catalog,
        () -> airbyteStateMessages.stream().map(AirbyteStateMessage::getStream).collect(Collectors.toList()),
        CURSOR_FUNCTION,
        CURSOR_FIELD_FUNCTION,
        CURSOR_RECORD_COUNT_FUNCTION,
        NAME_NAMESPACE_PAIR_FUNCTION);
  }

  @Override
  public CdcStateManager getCdcStateManager() {
    throw new UnsupportedOperationException("CDC state management not supported by stream state manager.");
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
            .withData(Jsons.jsonNode(StateGeneratorUtils.generateDbState(pairToCursorInfoMap)))
            .withStream(StateGeneratorUtils.generateStreamState(pair.get(), cursorInfo.get()));
      } else {
        LOGGER.warn("Cursor information could not be located in state for stream {}.  Returning a new, empty state message...", pair);
        return new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(new AirbyteStreamState());
      }
    } else {
      LOGGER.warn("Stream not provided.  Returning a new, empty state message...");
      return new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(new AirbyteStreamState());
    }
  }

}
