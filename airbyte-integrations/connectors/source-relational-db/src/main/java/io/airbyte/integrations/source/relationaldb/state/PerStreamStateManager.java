/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PerStreamStateManager extends AbstractStateManager<AirbyteStateMessage, AirbyteStreamState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(PerStreamStateManager.class);

  /**
   * {@link Function} that extracts the cursor from the stream state.
   */
  private static final Function<AirbyteStreamState, String> CURSOR_FUNCTION = stream -> {
    final Optional<DbStreamState> dbStreamState = extractState(stream);
    if (dbStreamState.isPresent()) {
      return dbStreamState.get().getCursor();
    } else {
      return null;
    }
  };

  /**
   * {@link Function} that extracts the cursor field(s) from the stream state.
   */
  private static final Function<AirbyteStreamState, List<String>> CURSOR_FIELD_FUNCTION = stream -> {
    final Optional<DbStreamState> dbStreamState = extractState(stream);
    if (dbStreamState.isPresent()) {
      return dbStreamState.get().getCursorField();
    } else {
      return List.of();
    }
  };

  /**
   * {@link Function} that creates an {@link AirbyteStreamNameNamespacePair} from the stream state.
   */
  private static final Function<AirbyteStreamState, AirbyteStreamNameNamespacePair> NAME_NAMESPACE_PAIR_FUNCTION =
      s -> new AirbyteStreamNameNamespacePair(s.getName(), s.getNamespace());

  /**
   * Constructs a new {@link PerStreamStateManager} that is seeded with the provided
   * {@link AirbyteStateMessage}.
   *
   * @param airbyteStateMessage The initial state represented as an {@link AirbyteStateMessage}.
   * @param catalog The {@link ConfiguredAirbyteCatalog} for the connector associated with this state
   *        manager.
   */
  public PerStreamStateManager(final AirbyteStateMessage airbyteStateMessage, final ConfiguredAirbyteCatalog catalog) {
    super(catalog,
        () -> airbyteStateMessage.getStreams(),
        CURSOR_FUNCTION,
        CURSOR_FIELD_FUNCTION,
        NAME_NAMESPACE_PAIR_FUNCTION);
  }

  @Override
  public CdcStateManager getCdcStateManager() {
    return new CdcStateManager(null);
  }

  @Override
  public AirbyteStateMessage toState() {
    final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairCursorInfoMap = getPairToCursorInfoMap();
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage();
    final List<AirbyteStreamState> airbyteStreamStates = generatePerStreamState(pairCursorInfoMap);

    // TODO detect global?

    return airbyteStateMessage.withStateType(AirbyteStateType.PER_STREAM).withStreams(airbyteStreamStates);
  }

  /**
   * Generates the per-stream state for each stream.
   *
   * @param pairCursorInfoMap The map of stream name/namespace to current cursor information.
   * @return The list of per-stream state.
   */
  private List<AirbyteStreamState> generatePerStreamState(final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairCursorInfoMap) {
    return pairCursorInfoMap.entrySet().stream()
        .filter(s -> s.getKey().getName() != null && s.getKey().getNamespace() != null)
        .sorted(Entry.comparingByKey()) // sort by stream name then namespace for sanity.
        .map(e -> new AirbyteStreamState()
            .withName(e.getKey().getName())
            .withNamespace(e.getKey().getNamespace())
            .withState(Jsons.jsonNode(generateDbStreamState(e.getKey(), e.getValue()))))
        .collect(Collectors.toList());
  }

  /**
   * Generates the {@link DbStreamState} for the given stream and cursor.
   *
   * @param airbyteStreamNameNamespacePair The stream.
   * @param cursorInfo The current cursor.
   * @return The {@link DbStreamState}.
   */
  private DbStreamState generateDbStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair, final CursorInfo cursorInfo) {
    return new DbStreamState()
        .withStreamName(airbyteStreamNameNamespacePair.getName())
        .withStreamNamespace(airbyteStreamNameNamespacePair.getNamespace())
        .withCursorField(cursorInfo.getCursorField() == null ? Collections.emptyList() : Lists.newArrayList(cursorInfo.getCursorField()))
        .withCursor(cursorInfo.getCursor());
  }

  /**
   * Extracts the actual state from the {@link AirbyteStreamState} object.
   *
   * @param state The {@link AirbyteStreamState} that contains the actual stream state as JSON.
   * @return An {@link Optional} possibly containing the deserialized representation of the stream
   *         state or an empty {@link Optional} if the state is not present or could not be
   *         deserialized.
   */
  private static Optional<DbStreamState> extractState(final AirbyteStreamState state) {
    try {
      return Optional.ofNullable(Jsons.object(state.getState(), DbStreamState.class));
    } catch (final IllegalArgumentException e) {
      LOGGER.error("Unable to extract state.", e);
      return Optional.empty();
    }
  }

}
