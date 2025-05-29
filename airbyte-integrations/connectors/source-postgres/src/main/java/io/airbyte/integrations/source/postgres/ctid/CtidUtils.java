/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.TableBlockSize;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcConnectorMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidUtils.class);
  public static final int POSTGRESQL_VERSION_TID_RANGE_SCAN_CAPABLE = 14;

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
                                                                        final Set<AirbyteStreamNameNamespacePair> streamPairs,
                                                                        final SyncMode syncMode) {

    return catalog.getStreams().stream()
        .filter(stream -> stream.getSyncMode() == syncMode)
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

  /**
   * Postgres servers version 14 and above are capable of running a tid range scan. Used by ctid
   * queries
   *
   * @param database database
   * @return true for Tid scan capable server
   */
  public static boolean isTidRangeScanCapableDBServer(final JdbcDatabase database) {
    try {
      return database.getMetaData().getDatabaseMajorVersion() >= POSTGRESQL_VERSION_TID_RANGE_SCAN_CAPABLE;
    } catch (final Exception e) {
      LOGGER.warn("Failed to get db server version", e);
    }
    return true;
  }

  public static PostgresCtidHandler createInitialLoader(final JdbcDatabase database,
                                                        final List<ConfiguredAirbyteStream> finalListOfStreamsToBeSyncedViaCtid,
                                                        final FileNodeHandler fileNodeHandler,
                                                        final String quoteString,
                                                        final CtidStateManager ctidStateManager,
                                                        Optional<PostgresCdcConnectorMetadataInjector> optionalMetadataInjector) {
    final JsonNode sourceConfig = database.getSourceConfig();

    final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes =
        PostgresQueryUtils.getTableBlockSizeForStreams(
            database,
            finalListOfStreamsToBeSyncedViaCtid,
            quoteString);

    final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, Integer> tablesMaxTuple =
        CtidUtils.isTidRangeScanCapableDBServer(database) ? null
            : PostgresQueryUtils.getTableMaxTupleForStreams(database, finalListOfStreamsToBeSyncedViaCtid, quoteString);

    return new PostgresCtidHandler(sourceConfig,
        database,
        new CtidPostgresSourceOperations(optionalMetadataInjector),
        quoteString,
        fileNodeHandler,
        tableBlockSizes,
        tablesMaxTuple,
        ctidStateManager);
  }

}
