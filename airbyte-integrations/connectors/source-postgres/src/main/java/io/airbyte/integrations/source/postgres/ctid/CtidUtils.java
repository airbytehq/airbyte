/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * The class mainly categorises the streams based on the state type into 3 categories: 1. Streams
 * that need to be synced via ctid iterator: - These are streams that are either newly added or did
 * not complete their initial sync. 2. Streams that need to be synced via xmin iterator: - These are
 * streams that have the xmin state_type that have completed their initial sync and are not syncing
 * data incrementally. 3. Streams that need to be synced via cursor-based iterator: - These are
 * streams that have the cursorBased state_type that have completed their initial sync and are not
 * syncing data incrementally.
 */
public class CtidUtils {

  public static List<ConfiguredAirbyteStream> identifyNewlyAddedStreams(final ConfiguredAirbyteCatalog fullCatalog,
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

  public record CtidStreams(List<ConfiguredAirbyteStream> streamsForCtidSync,
                            List<AirbyteStateMessage> statesFromCtidSync) {

  }

  public record StreamsCategorised<T> (CtidStreams ctidStreams,
                                       T remainingStreams) {

  }

}
