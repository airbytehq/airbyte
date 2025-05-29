/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore.initialsync;

import static io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialLoadStreamStateManager.PRIMARY_KEY_STATE_TYPE;
import static io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialLoadStreamStateManager.STATE_TYPE_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.singlestore.SingleStoreQueryUtils;
import io.airbyte.integrations.source.singlestore.SingleStoreType;
import io.airbyte.integrations.source.singlestore.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.singlestore.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreInitialReadUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreInitialReadUtil.class);

  /**
   * Determines the streams to sync for initial primary key load. These include streams that are (i)
   * currently in primary key load (ii) newly added incremental streams.
   */
  public static InitialLoadStreams streamsForInitialPrimaryKeyLoad(final StateManager stateManager, final ConfiguredAirbyteCatalog fullCatalog) {

    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final Set<AirbyteStreamNameNamespacePair> streamsStillInPkSync = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreamPairs = new HashSet<>();

    // Build a map of stream <-> initial load status for streams that currently have an initial primary
    // key load in progress.
    final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToInitialLoadStatus = new HashMap<>();
    if (rawStateMessages != null) {
      rawStateMessages.forEach(stateMessage -> {
        final AirbyteStreamState stream = stateMessage.getStream();
        final JsonNode streamState = stream.getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }
        final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace());
        // Build a map of stream <-> initial load status for streams that currently have an initial primary
        // key load in progress.
        if (streamState.has(STATE_TYPE_KEY)) {
          if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(PRIMARY_KEY_STATE_TYPE)) {
            final PrimaryKeyLoadStatus primaryKeyLoadStatus = Jsons.object(streamState, PrimaryKeyLoadStatus.class);
            pairToInitialLoadStatus.put(pair, primaryKeyLoadStatus);
            streamsStillInPkSync.add(pair);
          }
        }
        alreadySeenStreamPairs.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
      });
    }
    final List<ConfiguredAirbyteStream> streamsForPkSync = new ArrayList<>();

    fullCatalog.getStreams().stream()
        .filter(stream -> streamsStillInPkSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))).map(Jsons::clone)
        .forEach(streamsForPkSync::add);
    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyStreamsToSnapshot(fullCatalog,
        Collections.unmodifiableSet(alreadySeenStreamPairs));
    streamsForPkSync.addAll(newlyAddedStreams);
    return new InitialLoadStreams(
        streamsForPkSync.stream().filter(SingleStoreInitialReadUtil::streamHasPrimaryKey).collect(Collectors.toList()),
        pairToInitialLoadStatus);
  }

  public static List<ConfiguredAirbyteStream> identifyStreamsToSnapshot(
                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                        final Set<AirbyteStreamNameNamespacePair> alreadySyncedStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(
        catalog);
    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(
        Sets.difference(allStreams, alreadySyncedStreams));
    return catalog.getStreams().stream().filter(c -> c.getSyncMode() == SyncMode.INCREMENTAL)
        .filter(stream -> newlyAddedStreams.contains(
            AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
  }

  // Build a map of stream <-> primary key info (primary key field name + datatype) for all streams
  // currently undergoing initial primary key syncs.
  public static Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, PrimaryKeyInfo> initPairToPrimaryKeyInfoMap(
                                                                                                                           final JdbcDatabase database,
                                                                                                                           final InitialLoadStreams initialLoadStreams,
                                                                                                                           final Map<String, TableInfo<CommonField<SingleStoreType>>> tableNameToTable,
                                                                                                                           final String quoteString) {
    final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPkInfoMap = new HashMap<>();
    // For every stream that is in primary initial key sync, we want to maintain information about the
    // current primary key info associated with the
    // stream
    initialLoadStreams.streamsForInitialLoad().forEach(stream -> {
      final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair = new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(
          stream.getStream().getName(), stream.getStream().getNamespace());
      final PrimaryKeyInfo pkInfo = getPrimaryKeyInfo(database, stream, tableNameToTable, quoteString);
      pairToPkInfoMap.put(pair, pkInfo);
    });
    return pairToPkInfoMap;
  }

  // Returns the primary key info associated with the stream.
  private static PrimaryKeyInfo getPrimaryKeyInfo(final JdbcDatabase database,
                                                  final ConfiguredAirbyteStream stream,
                                                  final Map<String, TableInfo<CommonField<SingleStoreType>>> tableNameToTable,
                                                  final String quoteString) {
    // For cursor-based syncs, we cannot always assume a primary key field exists. We need to handle the
    // case where it does not exist when we support
    // cursor-based syncs.
    if (stream.getStream().getSourceDefinedPrimaryKey().size() > 1) {
      LOGGER.info("Composite primary key detected for {namespace, stream} : {}, {}", stream.getStream().getNamespace(), stream.getStream().getName());
    }
    final String pkFieldName = stream.getStream().getSourceDefinedPrimaryKey().get(0).get(0);
    final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getStream().getNamespace(),
        (stream.getStream().getName()));
    final TableInfo<CommonField<SingleStoreType>> table = tableNameToTable.get(fullyQualifiedTableName);
    final SingleStoreType pkFieldType = table.getFields().stream().filter(field -> field.getName().equals(pkFieldName)).findFirst().get().getType();

    final String pkMaxValue = SingleStoreQueryUtils.getMaxPkValueForStream(database, stream, pkFieldName, quoteString);
    return new PrimaryKeyInfo(pkFieldName, pkFieldType, pkMaxValue);
  }

  public static AirbyteStreamNameNamespacePair convertNameNamespacePairFromV0(
                                                                              final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair v1NameNamespacePair) {
    return new AirbyteStreamNameNamespacePair(v1NameNamespacePair.getName(), v1NameNamespacePair.getNamespace());
  }

  public static boolean isAnyStreamIncrementalSyncMode(ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode).anyMatch(syncMode -> syncMode == SyncMode.INCREMENTAL);
  }

  private static boolean streamHasPrimaryKey(final ConfiguredAirbyteStream stream) {
    return !stream.getStream().getSourceDefinedPrimaryKey().isEmpty();
  }

  public record InitialLoadStreams(List<ConfiguredAirbyteStream> streamsForInitialLoad,
                                   Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToInitialLoadStatus) {

  }

  public record CursorBasedStreams(List<ConfiguredAirbyteStream> streamsForCursorBased,
                                   Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus) {

  }

  public record PrimaryKeyInfo(String pkFieldName, SingleStoreType fieldType, String pkMaxValue) {

  }

}
