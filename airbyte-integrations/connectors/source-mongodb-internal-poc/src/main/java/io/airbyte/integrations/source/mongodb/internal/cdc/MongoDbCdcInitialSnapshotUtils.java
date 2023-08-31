/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.internal.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Utilities for determining the configured streams that should take part in the initial snapshot
 * portion of a CDC sync for MongoDB.
 */
public class MongoDbCdcInitialSnapshotUtils {

  private static final Predicate<ConfiguredAirbyteStream> SYNC_MODE_FILTER = c -> SyncMode.INCREMENTAL.equals(c.getSyncMode());

  /**
   * Returns the list of configured Airbyte streams that need to perform the initial snapshot portion
   * of a CDC sync. This includes streams that:
   * <ol>
   * <li>Did not complete a successful initial snapshot sync during the last execution</li>
   * <li>Have been added to the catalog since the last sync</li>
   * </ol>
   *
   * In addition, if the saved offset is no longer present in the server, all streams are used in the
   * initial snapshot in order to restore the offset to an existing value.
   *
   * @param stateManager The {@link MongoDbStateManager} that contains information about each stream's
   *        progress.
   * @param fullCatalog The fully configured Airbyte catalog.
   * @param savedOffsetIsValid Boolean value that indicates whether the offset exists on the server.
   *        If it does not exist, all streams will perform an initial sync.
   * @return The list of Airbyte streams to be used in the initial snapshot sync.
   */
  public static List<ConfiguredAirbyteStream> getStreamsForInitialSnapshot(final MongoDbStateManager stateManager,
                                                                           final ConfiguredAirbyteCatalog fullCatalog,
                                                                           final boolean savedOffsetIsValid) {

    if (!savedOffsetIsValid) {
      /*
       * If the saved offset does not exist on the server, re-sync everything via initial snapshot as we
       * have lost track of which changes have been processed already. This occurs when the oplog cycles
       * faster than a sync interval, resulting in the stored offset in our state being removed from the
       * oplog.
       */
      return fullCatalog.getStreams()
          .stream()
          .filter(SYNC_MODE_FILTER)
          .toList();
    } else {
      final List<ConfiguredAirbyteStream> initialSnapshotStreams = new ArrayList<>();

      // Find and filter out streams that have completed the initial snapshot
      final Set<AirbyteStreamNameNamespacePair> streamsStillInInitialSnapshot = stateManager.getStreamStates().entrySet().stream()
          .filter(e -> InitialSnapshotStatus.IN_PROGRESS.equals(e.getValue().status()))
          .map(Map.Entry::getKey)
          .collect(Collectors.toSet());

      // Fetch the streams from the catalog that still need to complete the initial snapshot sync
      initialSnapshotStreams.addAll(fullCatalog.getStreams().stream()
          .filter(stream -> streamsStillInInitialSnapshot.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
          .map(Jsons::clone)
          .toList());

      // Fetch the streams added to the catalog since the last sync
      initialSnapshotStreams.addAll(identifyStreamsToSnapshot(fullCatalog,
          new HashSet<>(stateManager.getStreamStates().keySet())));

      return initialSnapshotStreams;
    }

  }

  private static List<ConfiguredAirbyteStream> identifyStreamsToSnapshot(final ConfiguredAirbyteCatalog catalog,
                                                                         final Set<AirbyteStreamNameNamespacePair> alreadySyncedStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(Sets.difference(allStreams, alreadySyncedStreams));
    return catalog.getStreams().stream()
        .filter(SYNC_MODE_FILTER)
        .filter(stream -> newlyAddedStreams.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))).map(Jsons::clone)
        .toList();
  }

}
