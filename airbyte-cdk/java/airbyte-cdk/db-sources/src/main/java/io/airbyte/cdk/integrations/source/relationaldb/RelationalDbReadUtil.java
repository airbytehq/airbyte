/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb;

import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class RelationalDbReadUtil {

  public static List<ConfiguredAirbyteStream> identifyStreamsToSnapshot(final ConfiguredAirbyteCatalog catalog,
                                                                        final Set<AirbyteStreamNameNamespacePair> alreadySyncedStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(Sets.difference(allStreams, alreadySyncedStreams));
    return catalog.getStreams().stream()
        .filter(c -> c.getSyncMode() == SyncMode.INCREMENTAL)
        .filter(stream -> newlyAddedStreams.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
  }

  public static List<ConfiguredAirbyteStream> identifyStreamsForCursorBased(final ConfiguredAirbyteCatalog catalog,
                                                                            final List<ConfiguredAirbyteStream> streamsForInitialLoad) {

    final Set<AirbyteStreamNameNamespacePair> initialLoadStreamsNamespacePairs =
        streamsForInitialLoad.stream().map(stream -> AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))
            .collect(
                Collectors.toSet());
    return catalog.getStreams().stream()
        .filter(c -> c.getSyncMode() == SyncMode.INCREMENTAL)
        .filter(stream -> !initialLoadStreamsNamespacePairs.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
  }

  public static AirbyteStreamNameNamespacePair convertNameNamespacePairFromV0(final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair v1NameNamespacePair) {
    return new AirbyteStreamNameNamespacePair(v1NameNamespacePair.getName(), v1NameNamespacePair.getNamespace());
  }

}
