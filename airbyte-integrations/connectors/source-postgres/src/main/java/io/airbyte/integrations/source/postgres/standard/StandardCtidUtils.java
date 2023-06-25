package io.airbyte.integrations.source.postgres.standard;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
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

public class StandardCtidUtils {

  public static StreamsCategorised categoriseStreams(final StateManager stateManager,
                                                     final ConfiguredAirbyteCatalog fullCatalog) {
    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final List<AirbyteStateMessage> statesFromCtidSync = new ArrayList<>();
    final List<AirbyteStateMessage> statesFromStandardSync = new ArrayList<>();

    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreams = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> streamsStillInCtidSync = new HashSet<>();

    if (rawStateMessages != null) {
      rawStateMessages.forEach(stateMessage -> {
        final JsonNode streamState = stateMessage.getStream().getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        if (streamState.has("state_type")) {
          if (streamState.get("state_type").asText().equalsIgnoreCase("ctid")) {
            statesFromCtidSync.add(stateMessage);
            streamsStillInCtidSync.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
          } else if (streamState.get("state_type").asText().equalsIgnoreCase("standard")) {
            if (streamState.get("cursor").isNull()) {
              throw new RuntimeException("Null cursor value for the provided cursor column");
            }
            statesFromStandardSync.add(stateMessage);
          } else {
            throw new RuntimeException("Unknown state type: " + streamState.get("state_type").asText());
          }
        } else {
          throw new RuntimeException("State type not present");
        }
        alreadySeenStreams.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
      });
    }

    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyNewlyAddedStreams(fullCatalog, alreadySeenStreams);
    final List<ConfiguredAirbyteStream> streamsForCtidSync = new ArrayList<>();
    fullCatalog.getStreams().stream()
        .filter(stream -> streamsStillInCtidSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .forEach(streamsForCtidSync::add);

    streamsForCtidSync.addAll(newlyAddedStreams);

    final List<ConfiguredAirbyteStream> streamsForStandardSync = fullCatalog.getStreams().stream()
        .filter(stream -> !streamsForCtidSync.contains(stream))
        .map(Jsons::clone)
        .toList();

    return new StreamsCategorised(new CtidStreams(streamsForCtidSync, statesFromCtidSync),
                                  new StandardStreams(streamsForStandardSync, statesFromStandardSync));
  }


  private static final Logger LOGGER = LoggerFactory.getLogger(StandardCtidUtils.class);

  private static List<ConfiguredAirbyteStream> identifyNewlyAddedStreams(final ConfiguredAirbyteCatalog fullCatalog,
                                                                         final Set<AirbyteStreamNameNamespacePair> alreadySeenStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(fullCatalog);

    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(Sets.difference(allStreams, alreadySeenStreams));

    return fullCatalog.getStreams().stream()
        .filter(stream -> newlyAddedStreams.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
  }
  public record StreamsCategorised(StandardCtidUtils.CtidStreams ctidStreams,
                                   StandardCtidUtils.StandardStreams standardStreams) {

  }
  public record CtidStreams(List<ConfiguredAirbyteStream> streamsForCtidSync,
                            List<AirbyteStateMessage> statesFromCtidSync) {

  }

  public record StandardStreams(List<ConfiguredAirbyteStream> streamsForStandardSync,
                                List<AirbyteStateMessage> statesFromCtidSync) {

  }
}


