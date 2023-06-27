/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.postgres.xmin.PostgresXminHandler.shouldPerformFullSync;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The class mainly categorises the streams based on the state type into 3 categories:
 * 1. Streams that need to be synced via ctid iterator:
 * - These are streams that are either newly added or did not complete their initial sync.
 * 2. Streams that need to be synced via xmin iterator:
 * - These are streams that have the xmin state_type that have completed their initial sync and are not syncing data incrementally.
 * 3. Streams that need to be synced via standard iterator:
 * - These are streams that have the standard state_type that have completed their initial sync and are not syncing data incrementally.
 */
public class CtidUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidUtils.class);

  public static StreamsCategorised categoriseStreams(final StateManager stateManager,
                                                     final ConfiguredAirbyteCatalog fullCatalog,
                                                     final XminStatus currentXminStatus) {
    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final List<AirbyteStateMessage> statesFromCtidSync = new ArrayList<>();
    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreamPairs = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> stillInCtidStreamPairs = new HashSet<>();

    final List<AirbyteStateMessage> statesFromXminSync = new ArrayList<>();
    final Set<AirbyteStreamNameNamespacePair> xminSyncStreamPairs = new HashSet<>();

    final List<AirbyteStateMessage> statesFromStandardSync = new ArrayList<>();
    final Set<AirbyteStreamNameNamespacePair> standardSyncStreamPairs = new HashSet<>();

    if (rawStateMessages != null) {
      rawStateMessages.forEach(stateMessage -> {
        final JsonNode streamState = stateMessage.getStream().getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        if (streamState.has("state_type")) {
          final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
                                                                                         streamDescriptor.getNamespace());
          if (streamState.get("state_type").asText().equalsIgnoreCase("ctid")) {
            statesFromCtidSync.add(stateMessage);
            stillInCtidStreamPairs.add(pair);
          } else if (streamState.get("state_type").asText().equalsIgnoreCase("xmin")) {
            if (shouldPerformFullSync(currentXminStatus, streamState)) {
              LOGGER.info("Detected multiple wraparounds. Will perform a full sync for {}", pair);
              stillInCtidStreamPairs.add(pair);
            } else {
              xminSyncStreamPairs.add(pair);
              statesFromXminSync.add(stateMessage);
            }
          } else if (streamState.get("state_type").asText().equalsIgnoreCase("standard")) {
            if (streamState.get("cursor").isNull()) {
              throw new RuntimeException("Null cursor value for the provided cursor column");
            }
            standardSyncStreamPairs.add(pair);
            statesFromStandardSync.add(stateMessage);
          } else {
            throw new RuntimeException("Unknown state type: " + streamState.get("state_type").asText());
          }
        } else {
          throw new RuntimeException("State type not present");
        }
        alreadySeenStreamPairs.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
      });
    }

    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyNewlyAddedStreams(fullCatalog, alreadySeenStreamPairs);
    final List<ConfiguredAirbyteStream> streamsForCtidSync = getStreamsFromStreamPairs(fullCatalog, stillInCtidStreamPairs);
    streamsForCtidSync.addAll(newlyAddedStreams);

    final List<ConfiguredAirbyteStream> streamsForXminSync = getStreamsFromStreamPairs(fullCatalog, xminSyncStreamPairs);
    final List<ConfiguredAirbyteStream> streamsForStandardSync = getStreamsFromStreamPairs(fullCatalog, standardSyncStreamPairs);

    return new StreamsCategorised(new CtidStreams(streamsForCtidSync, statesFromCtidSync),
                                  new XminStreams(streamsForXminSync, statesFromXminSync),
                                  new StandardStreams(streamsForStandardSync, statesFromStandardSync));
  }

  private static List<ConfiguredAirbyteStream> identifyNewlyAddedStreams(final ConfiguredAirbyteCatalog fullCatalog,
                                                                         final Set<AirbyteStreamNameNamespacePair> alreadySeenStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(fullCatalog);

    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(Sets.difference(allStreams, alreadySeenStreams));

    return fullCatalog.getStreams().stream()
        .filter(stream -> newlyAddedStreams.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
  }

  public static List<ConfiguredAirbyteStream> getStreamsFromStreamPairs(final ConfiguredAirbyteCatalog catalog,
                                                                        final Set<AirbyteStreamNameNamespacePair> streamPairs) {

    return catalog.getStreams().stream()
        .filter(stream -> streamPairs.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
  }

  public record StreamsCategorised(CtidStreams ctidStreams,
                                   XminStreams xminStreams,
                                   StandardStreams standardStreams) {

  }

  public record CtidStreams(List<ConfiguredAirbyteStream> streamsForCtidSync,
                            List<AirbyteStateMessage> statesFromCtidSync) {

  }

  public record XminStreams(List<ConfiguredAirbyteStream> streamsForXminSync,
                            List<AirbyteStateMessage> statesFromXminSync) {

  }
  public record StandardStreams(List<ConfiguredAirbyteStream> streamsForStandardSync,
                                List<AirbyteStateMessage> statesFromCtidSync) {

  }
}
