/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.airbyte.integrations.source.postgres.ctid.CtidStateManager.STATE_TYPE_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class PostgresCdcCtidUtils {

  public static CtidStreams streamsToSyncViaCtid(final CdcStateManager stateManager,
                                                 final ConfiguredAirbyteCatalog fullCatalog,
                                                 final boolean savedOffsetAfterReplicationSlotLSN) {
    if (!savedOffsetAfterReplicationSlotLSN) {
      return new CtidStreams(
          fullCatalog.getStreams()
              .stream()
              .collect(Collectors.toList()),
          new HashMap<>());
    }

    final AirbyteStateMessage airbyteStateMessage = stateManager.getRawStateMessage();
    final Set<AirbyteStreamNameNamespacePair> streamsStillInCtidSync = new HashSet<>();
    final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus = new HashMap<>();
    if (airbyteStateMessage != null && airbyteStateMessage.getGlobal() != null && airbyteStateMessage.getGlobal().getStreamStates() != null) {
      airbyteStateMessage.getGlobal().getStreamStates().forEach(stateMessage -> {
        final JsonNode streamState = stateMessage.getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        if (streamState.has(STATE_TYPE_KEY)) {
          if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase("ctid")) {
            final CtidStatus ctidStatus = Jsons.object(streamState, CtidStatus.class);
            final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
                streamDescriptor.getNamespace());
            pairToCtidStatus.put(pair, ctidStatus);
            streamsStillInCtidSync.add(pair);
          }
        }
      });
    }

    final List<ConfiguredAirbyteStream> streamsForCtidSync = new ArrayList<>();
    fullCatalog.getStreams().stream()
        .filter(stream -> streamsStillInCtidSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .forEach(streamsForCtidSync::add);
    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyStreamsToSnapshot(fullCatalog, stateManager.getInitialStreamsSynced());
    streamsForCtidSync.addAll(newlyAddedStreams);

    return new CtidStreams(streamsForCtidSync, pairToCtidStatus);
  }

  private static List<ConfiguredAirbyteStream> identifyStreamsToSnapshot(final ConfiguredAirbyteCatalog catalog,
                                                                         final Set<AirbyteStreamNameNamespacePair> alreadySyncedStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(Sets.difference(allStreams, alreadySyncedStreams));
    return catalog.getStreams().stream()
        .filter(stream -> newlyAddedStreams.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))).map(Jsons::clone)
        .collect(Collectors.toList());
  }

  public record CtidStreams(List<ConfiguredAirbyteStream> streamsForCtidSync,
                            Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus) {

  }

}
