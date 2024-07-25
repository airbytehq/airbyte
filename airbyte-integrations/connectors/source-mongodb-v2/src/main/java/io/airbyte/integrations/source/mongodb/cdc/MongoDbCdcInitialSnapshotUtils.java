/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.PLATFORM_DATA_INCREASE_FACTOR;

import com.google.common.collect.Sets;
import com.mongodb.client.MongoClient;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.MongoUtil;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteEstimateTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utilities for determining the configured streams that should take part in the initial snapshot
 * portion of a CDC sync for MongoDB.
 */
public class MongoDbCdcInitialSnapshotUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcInitialSnapshotUtils.class);

  private static final Predicate<ConfiguredAirbyteStream> SYNC_MODE_FILTER = c -> SyncMode.INCREMENTAL.equals(c.getSyncMode());
  private static final Map<SyncMode, List<InitialSnapshotStatus>> syncModeToStatusValidationMap = Map.of(
      SyncMode.INCREMENTAL, List.of(InitialSnapshotStatus.IN_PROGRESS, InitialSnapshotStatus.COMPLETE),
      SyncMode.FULL_REFRESH, List.of(InitialSnapshotStatus.FULL_REFRESH));

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
   * @param mongoClient The {@link MongoClient} used to retrieve estimated trace statistics.
   * @param stateManager The {@link MongoDbStateManager} that contains information about each stream's
   *        progress.
   * @param fullCatalog The fully configured Airbyte catalog.
   * @param savedOffsetIsValid Boolean value that indicates whether the offset exists on the server.
   *        If it does not exist, all streams will perform an initial sync.
   * @return The list of Airbyte streams to be used in the initial snapshot sync.
   */
  public static List<ConfiguredAirbyteStream> getStreamsForInitialSnapshot(
                                                                           final MongoClient mongoClient,
                                                                           final MongoDbStateManager stateManager,
                                                                           final ConfiguredAirbyteCatalog fullCatalog,
                                                                           final boolean savedOffsetIsValid) {

    final List<ConfiguredAirbyteStream> initialSnapshotStreams = new ArrayList<>();

    if (!savedOffsetIsValid) {
      LOGGER.info("Offset state is invalid.  Add all {} stream(s) from the configured catalog to perform an initial snapshot.",
          fullCatalog.getStreams().size());

      /*
       * If the saved offset does not exist on the server, re-sync everything via initial snapshot as we
       * have lost track of which changes have been processed already. This occurs when the oplog cycles
       * faster than a sync interval, resulting in the stored offset in our state being removed from the
       * oplog.
       */
      initialSnapshotStreams.addAll(fullCatalog.getStreams()
          .stream()
          .filter(SYNC_MODE_FILTER)
          .toList());
    } else {
      // Find and filter out streams that have completed the initial snapshot
      final Set<AirbyteStreamNameNamespacePair> streamsStillInInitialSnapshot = stateManager.getStreamStates().entrySet().stream()
          .filter(e -> InitialSnapshotStatus.IN_PROGRESS.equals(e.getValue().status()))
          .map(Map.Entry::getKey)
          .collect(Collectors.toSet());

      LOGGER.info("There are {} stream(s) that are still in progress of an initial snapshot sync.", streamsStillInInitialSnapshot.size());

      // Fetch the streams from the catalog that still need to complete the initial snapshot sync
      initialSnapshotStreams.addAll(fullCatalog.getStreams().stream()
          .filter(stream -> streamsStillInInitialSnapshot.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
          .map(Jsons::clone)
          .toList());

      // Fetch the streams added to the catalog since the last sync
      final List<ConfiguredAirbyteStream> newStreams = identifyStreamsToSnapshot(fullCatalog,
          new HashSet<>(stateManager.getStreamStates().keySet()));
      LOGGER.info("There are {} stream(s) that have been added to the catalog since the last sync.", newStreams.size());
      initialSnapshotStreams.addAll(newStreams);
    }

    // Emit estimated trace message for each stream that will perform an initial snapshot sync
    initialSnapshotStreams.forEach(s -> estimateInitialSnapshotSyncSize(mongoClient, s));

    return initialSnapshotStreams;
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

  private static void estimateInitialSnapshotSyncSize(final MongoClient mongoClient, final ConfiguredAirbyteStream stream) {
    final Optional<MongoUtil.CollectionStatistics> collectionStatistics =
        MongoUtil.getCollectionStatistics(mongoClient.getDatabase(stream.getStream().getNamespace()), stream);
    collectionStatistics.ifPresent(c -> {
      AirbyteTraceMessageUtility.emitEstimateTrace(PLATFORM_DATA_INCREASE_FACTOR * c.size().longValue(),
          AirbyteEstimateTraceMessage.Type.STREAM, c.count().longValue(), stream.getStream().getName(), stream.getStream().getNamespace());
      LOGGER
          .info(String.format(
              "Estimate for table: %s.%s : {sync_row_count: %s, sync_bytes: %s, total_table_row_count: %s, total_table_bytes: %s}",
              stream.getStream().getNamespace(), stream.getStream().getName(), c.count(), c.size(), c.count(), c.size()));
    });
  }

  private static boolean isValidInitialSnapshotStatus(final SyncMode syncMode, final MongoDbStreamState state) {
    return syncModeToStatusValidationMap.get(syncMode).contains(state.status());
  }

  public static void validateStateSyncMode(final MongoDbStateManager stateManager, final List<ConfiguredAirbyteStream> streams) {
    streams.forEach(stream -> {
      final var existingState = stateManager.getStreamState(stream.getStream().getName(), stream.getStream().getNamespace());
      if (existingState.isPresent() && !isValidInitialSnapshotStatus(stream.getSyncMode(), existingState.get())) {
        throw new ConfigErrorException("Stream " + stream.getStream().getName() + " is " + stream.getSyncMode() + " but the saved status "
            + existingState.get().status() + " doesn't match. Please reset this stream");
      }
    });
  }

}
