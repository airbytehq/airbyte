package io.airbyte.integrations.source.postgres.xmin;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
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

public class XminCtidUtils {
  private static final Logger LOGGER = LoggerFactory.getLogger(XminCtidUtils.class);

  public static StreamsCategorised categoriseStreams(final StateManager stateManager, final ConfiguredAirbyteCatalog fullCatalog, final XminStatus currentXminStatus) {
    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final List<AirbyteStateMessage> statesFromCtidSync = new ArrayList<>();
    final List<AirbyteStateMessage> statesFromXminSync = new ArrayList<>();

    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreams = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> streamsStillInCtidSync = new HashSet<>();

    if (rawStateMessages != null) {
      rawStateMessages.forEach(s -> {
        final JsonNode streamState = s.getStream().getStreamState();
        final StreamDescriptor streamDescriptor = s.getStream().getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }
        final AirbyteStateMessage clonedState = Jsons.clone(s);
        if (streamState.has("state_type") && streamState.get("state_type").asText().equalsIgnoreCase("ctid")) {
          statesFromCtidSync.add(clonedState);
          streamsStillInCtidSync.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
        } else if (shouldPerformFullSync(currentXminStatus, streamState)) {
          final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
              streamDescriptor.getNamespace());
          LOGGER.info("Detected multiple wraparounds. Will perform a full sync for {}", pair);
          streamsStillInCtidSync.add(pair);
        } else {
          statesFromXminSync.add(clonedState);
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

    final List<ConfiguredAirbyteStream> streamsForXminSync = fullCatalog.getStreams().stream()
        .filter(stream -> !streamsForCtidSync.contains(stream))
        .map(Jsons::clone)
        .toList();

    return new StreamsCategorised(new CtidStreams(streamsForCtidSync, statesFromCtidSync), new XminStreams(streamsForXminSync, statesFromXminSync));
  }

  @VisibleForTesting
  static boolean shouldPerformFullSync(final XminStatus currentXminStatus, final JsonNode streamState) {
    // Detects whether source Postgres DB has undergone multiple wraparound events between syncs.
    return streamState.has("num_wraparound") && (currentXminStatus.getNumWraparound() - streamState.get("num_wraparound").asLong() >= 2);
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


  public static class StreamsCategorised {

    public final CtidStreams ctidStreams;
    public final XminStreams xminStreams;

    public StreamsCategorised(final CtidStreams ctidStreams, final XminStreams xminStreams) {
      this.ctidStreams = ctidStreams;
      this.xminStreams = xminStreams;
    }
  }

  public static class CtidStreams {

    public final List<ConfiguredAirbyteStream> streamsForCtidSync;
    public final List<AirbyteStateMessage> statesFromCtidSync;

    public CtidStreams(final List<ConfiguredAirbyteStream> streamsForCtidSync,
        final List<AirbyteStateMessage> statesFromCtidSync) {
      this.streamsForCtidSync = streamsForCtidSync;
      this.statesFromCtidSync = statesFromCtidSync;
    }
  }

  public static class XminStreams {

    public final List<ConfiguredAirbyteStream> streamsForXminSync;
    public final List<AirbyteStateMessage> statesFromXminSync;

    public XminStreams(final List<ConfiguredAirbyteStream> streamsForXminSync,
        final List<AirbyteStateMessage> statesFromXminSync) {
      this.streamsForXminSync = streamsForXminSync;
      this.statesFromXminSync = statesFromXminSync;
    }
  }

}
