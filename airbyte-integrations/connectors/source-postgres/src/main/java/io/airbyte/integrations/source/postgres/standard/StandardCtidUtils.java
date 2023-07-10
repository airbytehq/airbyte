/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.standard;

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
 * The class mainly categorises the streams based on the state type into two categories :
 * 1. Streams that need to be synced via ctid iterator: These are streams that are either newly added or did
 * not complete their initial sync.
 * 2. Streams that need to be synced via standard cursor-based iterator:
 * These are streams that have completed their initial sync and are not syncing data incrementally.
 */
public class StandardCtidUtils {
  private static final Logger LOGGER = LoggerFactory.getLogger(StandardCtidUtils.class);
  public static StreamsCategorised<StandardStreams> categoriseStreams(final StateManager stateManager,
                                                                      final ConfiguredAirbyteCatalog fullCatalog) {
    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final List<AirbyteStateMessage> statesFromCtidSync = new ArrayList<>();
    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreamPairs = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> stillInCtidStreamPairs = new HashSet<>();

    final List<AirbyteStateMessage> statesFromStandardSync = new ArrayList<>();
    final Set<AirbyteStreamNameNamespacePair> standardSyncStreamPairs = new HashSet<>();

    if (rawStateMessages != null) {
      rawStateMessages.forEach(stateMessage -> {
        final JsonNode streamState = stateMessage.getStream().getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
                                                                                       streamDescriptor.getNamespace());

        if (streamState.has("state_type")) {
          if (streamState.get("state_type").asText().equalsIgnoreCase(StateType.CTID.value())) {
            statesFromCtidSync.add(stateMessage);
            stillInCtidStreamPairs.add(pair);
          } else if (streamState.get("state_type").asText().equalsIgnoreCase(StateType.STANDARD.value())) {
            standardSyncStreamPairs.add(pair);
            statesFromStandardSync.add(stateMessage);
          } else {
            throw new RuntimeException("Unknown state type: " + streamState.get("state_type").asText());
          }
        } else {
          LOGGER.info("State type not present, syncing stream {} via standard method", streamDescriptor.getName());
          standardSyncStreamPairs.add(pair);
          statesFromStandardSync.add(stateMessage);
        }
        alreadySeenStreamPairs.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
      });
    }

    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyNewlyAddedStreams(fullCatalog, alreadySeenStreamPairs);
    final List<ConfiguredAirbyteStream> streamsForCtidSync = getStreamsFromStreamPairs(fullCatalog, stillInCtidStreamPairs);
    streamsForCtidSync.addAll(newlyAddedStreams);

    final List<ConfiguredAirbyteStream> streamsForStandardSync = getStreamsFromStreamPairs(fullCatalog, standardSyncStreamPairs);

    return new StreamsCategorised<>(new CtidStreams(streamsForCtidSync, statesFromCtidSync),
        new StandardStreams(streamsForStandardSync, statesFromStandardSync));
  }

  public record StandardStreams(List<ConfiguredAirbyteStream> streamsForStandardSync,
                                List<AirbyteStateMessage> statesFromStandardSync) {
  }

  /**
   * Reclassifies previously categorised ctid stream into standard category.
   * Used in case we identify ctid is not possible such as a View
   * @param categorisedStreams categorised streams
   * @param streamPair stream to reclassify
   */
  public static void reclassifyCategorisedCtidStream(final StreamsCategorised<StandardStreams> categorisedStreams, AirbyteStreamNameNamespacePair streamPair) {
    final Optional<ConfiguredAirbyteStream> foundStream = categorisedStreams
        .ctidStreams()
        .streamsForCtidSync().stream().filter(c -> Objects.equals(
            streamPair,
            new AirbyteStreamNameNamespacePair(c.getStream().getName(), c.getStream().getNamespace())))
        .findFirst();
    foundStream.ifPresent(c -> {
      categorisedStreams.remainingStreams().streamsForStandardSync().add(c);
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
      categorisedStreams.remainingStreams().statesFromStandardSync().add(m);
      categorisedStreams.ctidStreams().statesFromCtidSync().remove(m);
    });
  }

  public static void reclassifyCategorisedCtidStreams(final StreamsCategorised<StandardStreams> categorisedStreams, List<AirbyteStreamNameNamespacePair> streamPairs) {
    streamPairs.forEach(c -> reclassifyCategorisedCtidStream(categorisedStreams, c));
  }
}
