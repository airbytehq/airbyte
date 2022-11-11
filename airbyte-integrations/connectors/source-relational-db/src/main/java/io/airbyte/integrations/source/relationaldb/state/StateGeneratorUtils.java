/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Collection of utilities that facilitate the generation of state objects.
 */
public class StateGeneratorUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateGeneratorUtils.class);

  /**
   * {@link Function} that extracts the cursor from the stream state.
   */
  public static final Function<AirbyteStreamState, String> CURSOR_FUNCTION = stream -> {
    final Optional<DbStreamState> dbStreamState = StateGeneratorUtils.extractState(stream);
    return dbStreamState.map(DbStreamState::getCursor).orElse(null);
  };

  /**
   * {@link Function} that extracts the cursor field(s) from the stream state.
   */
  public static final Function<AirbyteStreamState, List<String>> CURSOR_FIELD_FUNCTION = stream -> {
    final Optional<DbStreamState> dbStreamState = StateGeneratorUtils.extractState(stream);
    if (dbStreamState.isPresent()) {
      return dbStreamState.get().getCursorField();
    } else {
      return List.of();
    }
  };

  /**
   * {@link Function} that creates an {@link AirbyteStreamNameNamespacePair} from the stream state.
   */
  public static final Function<AirbyteStreamState, AirbyteStreamNameNamespacePair> NAME_NAMESPACE_PAIR_FUNCTION =
      s -> isValidStreamDescriptor(s.getStreamDescriptor())
          ? new AirbyteStreamNameNamespacePair(s.getStreamDescriptor().getName(), s.getStreamDescriptor().getNamespace())
          : null;

  private StateGeneratorUtils() {}

  /**
   * Generates the stream state for the given stream and cursor information.
   *
   * @param airbyteStreamNameNamespacePair The stream.
   * @param cursorInfo The current cursor.
   * @return The {@link AirbyteStreamState} representing the current state of the stream.
   */
  public static AirbyteStreamState generateStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                                       final CursorInfo cursorInfo) {
    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(airbyteStreamNameNamespacePair.getName()).withNamespace(airbyteStreamNameNamespacePair.getNamespace()))
        .withStreamState(Jsons.jsonNode(generateDbStreamState(airbyteStreamNameNamespacePair, cursorInfo)));
  }

  /**
   * Generates a list of valid stream states from the provided stream and cursor information. A stream
   * state is considered to be valid if the stream has a valid descriptor (see
   * {@link #isValidStreamDescriptor(StreamDescriptor)} for more details).
   *
   * @param pairToCursorInfoMap The map of stream name/namespace tuple to the current cursor
   *        information for that stream
   * @return The list of stream states derived from the state information extracted from the provided
   *         map.
   */
  public static List<AirbyteStreamState> generateStreamStateList(final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfoMap) {
    return pairToCursorInfoMap.entrySet().stream()
        .sorted(Entry.comparingByKey())
        .map(e -> generateStreamState(e.getKey(), e.getValue()))
        .filter(s -> isValidStreamDescriptor(s.getStreamDescriptor()))
        .collect(Collectors.toList());
  }

  /**
   * Generates the legacy global state for backwards compatibility.
   *
   * @param pairToCursorInfoMap The map of stream name/namespace tuple to the current cursor
   *        information for that stream
   * @return The legacy {@link DbState}.
   */
  public static DbState generateDbState(final Map<AirbyteStreamNameNamespacePair, CursorInfo> pairToCursorInfoMap) {
    return new DbState()
        .withCdc(false)
        .withStreams(pairToCursorInfoMap.entrySet().stream()
            .sorted(Entry.comparingByKey()) // sort by stream name then namespace for sanity.
            .map(e -> generateDbStreamState(e.getKey(), e.getValue()))
            .collect(Collectors.toList()));
  }

  /**
   * Generates the {@link DbStreamState} for the given stream and cursor.
   *
   * @param airbyteStreamNameNamespacePair The stream.
   * @param cursorInfo The current cursor.
   * @return The {@link DbStreamState}.
   */
  public static DbStreamState generateDbStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                                    final CursorInfo cursorInfo) {
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
  public static Optional<DbStreamState> extractState(final AirbyteStreamState state) {
    try {
      return Optional.ofNullable(Jsons.object(state.getStreamState(), DbStreamState.class));
    } catch (final IllegalArgumentException e) {
      LOGGER.error("Unable to extract state.", e);
      return Optional.empty();
    }
  }

  /**
   * Tests whether the provided {@link StreamDescriptor} is valid. A valid descriptor is defined as
   * one that has a non-{@code null} name.
   *
   * See
   * https://github.com/airbytehq/airbyte/blob/e63458fabb067978beb5eaa74d2bc130919b419f/docs/understanding-airbyte/airbyte-protocol.md
   * for more details
   *
   * @param streamDescriptor A {@link StreamDescriptor} to be validated.
   * @return {@code true} if the provided {@link StreamDescriptor} is valid or {@code false} if it is
   *         invalid.
   */
  public static boolean isValidStreamDescriptor(final StreamDescriptor streamDescriptor) {
    if (streamDescriptor != null) {
      return streamDescriptor.getName() != null;
    } else {
      return false;
    }
  }

  /**
   * Converts a {@link AirbyteStateType#LEGACY} state message into a {@link AirbyteStateType#GLOBAL}
   * message.
   *
   * @param airbyteStateMessage A {@link AirbyteStateType#LEGACY} state message.
   * @return A {@link AirbyteStateType#GLOBAL} state message.
   */
  public static AirbyteStateMessage convertLegacyStateToGlobalState(final AirbyteStateMessage airbyteStateMessage) {
    final DbState dbState = Jsons.object(airbyteStateMessage.getData(), DbState.class);
    final AirbyteGlobalState globalState = new AirbyteGlobalState()
        .withSharedState(Jsons.jsonNode(dbState.getCdcState()))
        .withStreamStates(dbState.getStreams().stream()
            .map(s -> new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(s.getStreamName()).withNamespace(s.getStreamNamespace()))
                .withStreamState(Jsons.jsonNode(s)))
            .collect(
                Collectors.toList()));
    return new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState);
  }

  /**
   * Converts a {@link AirbyteStateType#LEGACY} state message into a list of
   * {@link AirbyteStateType#STREAM} messages.
   *
   * @param airbyteStateMessage A {@link AirbyteStateType#LEGACY} state message.
   * @return A list {@link AirbyteStateType#STREAM} state messages.
   */
  public static List<AirbyteStateMessage> convertLegacyStateToStreamState(final AirbyteStateMessage airbyteStateMessage) {
    return Jsons.object(airbyteStateMessage.getData(), DbState.class).getStreams().stream()
        .map(s -> new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withNamespace(s.getStreamNamespace()).withName(s.getStreamName()))
                .withStreamState(Jsons.jsonNode(s))))
        .collect(Collectors.toList());
  }

}
