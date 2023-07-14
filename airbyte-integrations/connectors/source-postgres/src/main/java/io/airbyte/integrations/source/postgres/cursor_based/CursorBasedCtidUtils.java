/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cursor_based;

import static io.airbyte.integrations.source.postgres.ctid.CtidStateManager.STATE_TYPE_KEY;
import static io.airbyte.integrations.source.postgres.ctid.CtidUtils.getStreamsFromStreamPairs;
import static io.airbyte.integrations.source.postgres.ctid.CtidUtils.identifyNewlyAddedStreams;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.postgres.ctid.CtidUtils.CtidStreams;
import io.airbyte.integrations.source.postgres.ctid.CtidUtils.StreamsCategorised;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The class mainly categorises the streams based on the state type into two categories : 1. Streams
 * that need to be synced via ctid iterator: These are streams that are either newly added or did
 * not complete their initial sync. 2. Streams that need to be synced via cursor-based
 * iterator: These are streams that have completed their initial sync and are not syncing data
 * incrementally.
 */
public class CursorBasedCtidUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(CursorBasedCtidUtils.class);

  public static StreamsCategorised<CursorBasedStreams> categoriseStreams(final StateManager stateManager,
                                                                         final ConfiguredAirbyteCatalog fullCatalog) {
    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final List<AirbyteStateMessage> statesFromCtidSync = new ArrayList<>();
    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreamPairs = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> stillInCtidStreamPairs = new HashSet<>();

    final List<AirbyteStateMessage> statesFromCursorBasedSync = new ArrayList<>();
    final Set<AirbyteStreamNameNamespacePair> cursorBasedSyncStreamPairs = new HashSet<>();

    if (rawStateMessages != null) {
      rawStateMessages.forEach(stateMessage -> {
        final JsonNode streamState = stateMessage.getStream().getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
            streamDescriptor.getNamespace());

        if (streamState.has(STATE_TYPE_KEY)) {
          if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(StateType.CTID.value())) {
            statesFromCtidSync.add(stateMessage);
            stillInCtidStreamPairs.add(pair);
          } else if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(StateType.CURSOR_BASED.value())) {
            cursorBasedSyncStreamPairs.add(pair);
            statesFromCursorBasedSync.add(stateMessage);
          } else {
            throw new RuntimeException("Unknown state type: " + streamState.get(STATE_TYPE_KEY).asText());
          }
        } else {
          LOGGER.info("State type not present, syncing stream {} via cursor", streamDescriptor.getName());
          cursorBasedSyncStreamPairs.add(pair);
          statesFromCursorBasedSync.add(stateMessage);
        }
        alreadySeenStreamPairs.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
      });
    }

    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyNewlyAddedStreams(fullCatalog, alreadySeenStreamPairs);
    final List<ConfiguredAirbyteStream> streamsForCtidSync = getStreamsFromStreamPairs(fullCatalog, stillInCtidStreamPairs);
    streamsForCtidSync.addAll(newlyAddedStreams);

    final List<ConfiguredAirbyteStream> streamsForCursorBasedSync = getStreamsFromStreamPairs(fullCatalog, cursorBasedSyncStreamPairs);

    return new StreamsCategorised<>(new CtidStreams(streamsForCtidSync, statesFromCtidSync),
        new CursorBasedStreams(streamsForCursorBasedSync, statesFromCursorBasedSync));
  }

  public record CursorBasedStreams(List<ConfiguredAirbyteStream> streamsForCursorBasedSync,
                                   List<AirbyteStateMessage> statesFromCursorBasedSync) {}

  /**
   * Reclassifies previously categorised ctid stream into standard category.
   * Used in case we identify ctid is not possible such as a View
   * @param categorisedStreams categorised streams
   * @param streamPair stream to reclassify
   */
  public static void reclassifyCategorisedCtidStream(final StreamsCategorised<CursorBasedStreams> categorisedStreams, AirbyteStreamNameNamespacePair streamPair) {
    final Optional<ConfiguredAirbyteStream> foundStream = categorisedStreams
        .ctidStreams()
        .streamsForCtidSync().stream().filter(c -> Objects.equals(
            streamPair,
            new AirbyteStreamNameNamespacePair(c.getStream().getName(), c.getStream().getNamespace())))
        .findFirst();
    foundStream.ifPresent(c -> {
      categorisedStreams.remainingStreams().streamsForCursorBasedSync().add(c);
      categorisedStreams.ctidStreams().streamsForCtidSync().remove(c);
      LOGGER.info("Reclassified {}.{} as standard stream", c.getStream().getNamespace(), c.getStream().getName());
    });

    // Should there ever be a matching ctid state when ctid is not possible?
    final Optional<AirbyteStateMessage> foundStateMessage = categorisedStreams
        .ctidStreams()
        .statesFromCtidSync().stream().filter(m -> Objects.equals(streamPair,
            new AirbyteStreamNameNamespacePair(
                m.getStream().getStreamDescriptor().getName(),
                m.getStream().getStreamDescriptor().getNamespace())))
        .findFirst();
    foundStateMessage.ifPresent(m -> {
      categorisedStreams.remainingStreams().statesFromCursorBasedSync().add(m);
      categorisedStreams.ctidStreams().statesFromCtidSync().remove(m);
    });
  }

  public static void reclassifyCategorisedCtidStreams(final StreamsCategorised<CursorBasedStreams> categorisedStreams, List<AirbyteStreamNameNamespacePair> streamPairs) {
    streamPairs.forEach(c -> reclassifyCategorisedCtidStream(categorisedStreams, c));
  }
}
