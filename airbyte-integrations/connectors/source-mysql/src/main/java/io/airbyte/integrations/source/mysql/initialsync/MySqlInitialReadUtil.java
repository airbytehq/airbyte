/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import static io.airbyte.cdk.integrations.debezium.internals.mysql.MysqlCdcStateConstants.MYSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mysql.MySqlQueryUtils.getTableSizeInfoForStreams;
import static io.airbyte.integrations.source.mysql.MySqlQueryUtils.prettyPrintConfiguredAirbyteStreamList;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadGlobalStateManager.STATE_TYPE_KEY;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.PRIMARY_KEY_STATE_TYPE;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import com.mysql.cj.MysqlType;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.FirstRecordWaitTimeUtil;
import io.airbyte.cdk.integrations.debezium.internals.mysql.MySqlCdcPosition;
import io.airbyte.cdk.integrations.debezium.internals.mysql.MySqlCdcTargetPosition;
import io.airbyte.cdk.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil;
import io.airbyte.cdk.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes;
import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mysql.MySqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mysql.MySqlCdcProperties;
import io.airbyte.integrations.source.mysql.MySqlCdcSavedInfoFetcher;
import io.airbyte.integrations.source.mysql.MySqlCdcStateHandler;
import io.airbyte.integrations.source.mysql.MySqlQueryUtils;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadSourceOperations.CdcMetadataInjector;
import io.airbyte.integrations.source.mysql.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlInitialReadUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialReadUtil.class);

  /*
   * Returns the read iterators associated with : 1. Initial cdc read snapshot via primary key
   * queries. 2. Incremental cdc reads via debezium.
   *
   * The initial load iterators need to always be run before the incremental cdc iterators. This is to
   * prevent advancing the binlog offset in the state before all streams have snapshotted. Otherwise,
   * there could be data loss.
   */
  public static List<AutoCloseableIterator<AirbyteMessage>> getCdcReadIterators(final JdbcDatabase database,
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                                                                final StateManager stateManager,
                                                                                final Instant emittedAt,
                                                                                final String quoteString) {
    final JsonNode sourceConfig = database.getSourceConfig();
    final Duration firstRecordWaitTime = FirstRecordWaitTimeUtil.getFirstRecordWaitTime(sourceConfig);
    LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
    // Determine the streams that need to be loaded via primary key sync.
    final List<AutoCloseableIterator<AirbyteMessage>> initialLoadIterator = new ArrayList<>();

    // Construct the initial state for MySQL. If there is already existing state, we use that instead
    // since that is associated with the debezium
    // state associated with the initial sync.
    final MySqlDebeziumStateUtil mySqlDebeziumStateUtil = new MySqlDebeziumStateUtil();
    final JsonNode initialDebeziumState = mySqlDebeziumStateUtil.constructInitialDebeziumState(
        MySqlCdcProperties.getDebeziumProperties(database), catalog, database);

    final JsonNode state =
        (stateManager.getCdcStateManager().getCdcState() == null || stateManager.getCdcStateManager().getCdcState().getState() == null)
            ? initialDebeziumState
            : Jsons.clone(stateManager.getCdcStateManager().getCdcState().getState());

    final Optional<MysqlDebeziumStateAttributes> savedOffset = mySqlDebeziumStateUtil.savedOffset(
        MySqlCdcProperties.getDebeziumProperties(database), catalog, state.get(MYSQL_CDC_OFFSET), sourceConfig);

    final boolean savedOffsetStillPresentOnServer =
        savedOffset.isPresent() && mySqlDebeziumStateUtil.savedOffsetStillPresentOnServer(database, savedOffset.get());

    if (!savedOffsetStillPresentOnServer) {
      LOGGER.warn("Saved offset no longer present on the server, Airbyte is going to trigger a sync from scratch");
    }

    final InitialLoadStreams initialLoadStreams = cdcStreamsForInitialPrimaryKeyLoad(stateManager.getCdcStateManager(), catalog,
        savedOffsetStillPresentOnServer);

    final CdcState stateToBeUsed = (!savedOffsetStillPresentOnServer || (stateManager.getCdcStateManager().getCdcState() == null
        || stateManager.getCdcStateManager().getCdcState().getState() == null)) ? new CdcState().withState(initialDebeziumState)
            : stateManager.getCdcStateManager().getCdcState();

    final MySqlCdcConnectorMetadataInjector metadataInjector = MySqlCdcConnectorMetadataInjector.getInstance(emittedAt);

    // If there are streams to sync via primary key load, build the relevant iterators.
    if (!initialLoadStreams.streamsForInitialLoad().isEmpty()) {
      LOGGER.info("Streams to be synced via primary key : {}", initialLoadStreams.streamsForInitialLoad().size());
      LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(initialLoadStreams.streamsForInitialLoad()));
      final MySqlInitialLoadStateManager initialLoadStateManager =
          new MySqlInitialLoadGlobalStateManager(initialLoadStreams,
              initPairToPrimaryKeyInfoMap(database, initialLoadStreams, tableNameToTable, quoteString),
              stateToBeUsed, catalog);
      final MysqlDebeziumStateAttributes stateAttributes = MySqlDebeziumStateUtil.getStateAttributesFromDB(database);

      final MySqlInitialLoadSourceOperations sourceOperations =
          new MySqlInitialLoadSourceOperations(
              Optional.of(new CdcMetadataInjector(emittedAt.toString(), stateAttributes, metadataInjector)));
      final MySqlInitialLoadHandler initialLoadHandler = new MySqlInitialLoadHandler(sourceConfig, database,
          sourceOperations,
          quoteString,
          initialLoadStateManager,
          namespacePair -> Jsons.emptyObject(),
          getTableSizeInfoForStreams(database, initialLoadStreams.streamsForInitialLoad(), quoteString));

      initialLoadIterator.addAll(initialLoadHandler.getIncrementalIterators(
          new ConfiguredAirbyteCatalog().withStreams(initialLoadStreams.streamsForInitialLoad()),
          tableNameToTable,
          emittedAt));
    } else {
      LOGGER.info("No streams will be synced via primary key");
    }

    // Build the incremental CDC iterators.
    final AirbyteDebeziumHandler<MySqlCdcPosition> handler =
        new AirbyteDebeziumHandler<>(sourceConfig, MySqlCdcTargetPosition.targetPosition(database), true, firstRecordWaitTime, OptionalInt.empty());

    final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
        new MySqlCdcSavedInfoFetcher(stateToBeUsed),
        new MySqlCdcStateHandler(stateManager),
        metadataInjector,
        MySqlCdcProperties.getDebeziumProperties(database),
        DebeziumPropertiesManager.DebeziumConnectorType.RELATIONALDB,
        emittedAt,
        false);

    // This starts processing the binglogs as soon as initial sync is complete, this is a bit different
    // from the current cdc syncs.
    // We finish the current CDC once the initial snapshot is complete and the next sync starts
    // processing the binlogs
    return Collections.singletonList(
        AutoCloseableIterators.concatWithEagerClose(
            Stream
                .of(initialLoadIterator, Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)))
                .flatMap(Collection::stream)
                .collect(Collectors.toList()),
            AirbyteTraceMessageUtility::emitStreamStatusTrace));
  }

  /**
   * CDC specific: Determines the streams to sync for initial primary key load. These include streams
   * that are (i) currently in primary key load (ii) newly added incremental streams.
   */
  public static InitialLoadStreams cdcStreamsForInitialPrimaryKeyLoad(final CdcStateManager stateManager,
                                                                      final ConfiguredAirbyteCatalog fullCatalog,
                                                                      final boolean savedOffsetStillPresentOnServer) {
    if (!savedOffsetStillPresentOnServer) {
      return new InitialLoadStreams(
          fullCatalog.getStreams()
              .stream()
              .filter(c -> c.getSyncMode() == SyncMode.INCREMENTAL)
              .collect(Collectors.toList()),
          new HashMap<>());
    }

    final AirbyteStateMessage airbyteStateMessage = stateManager.getRawStateMessage();
    final Set<AirbyteStreamNameNamespacePair> streamsStillinPkSync = new HashSet<>();

    // Build a map of stream <-> initial load status for streams that currently have an initial primary
    // key load in progress.
    final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToInitialLoadStatus = new HashMap<>();
    if (airbyteStateMessage != null && airbyteStateMessage.getGlobal() != null && airbyteStateMessage.getGlobal().getStreamStates() != null) {
      airbyteStateMessage.getGlobal().getStreamStates().forEach(stateMessage -> {
        final JsonNode streamState = stateMessage.getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        if (streamState.has(STATE_TYPE_KEY)) {
          if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(PRIMARY_KEY_STATE_TYPE)) {
            final PrimaryKeyLoadStatus primaryKeyLoadStatus = Jsons.object(streamState, PrimaryKeyLoadStatus.class);
            final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
                streamDescriptor.getNamespace());
            pairToInitialLoadStatus.put(pair, primaryKeyLoadStatus);
            streamsStillinPkSync.add(pair);
          }
        }
      });
    }

    final List<ConfiguredAirbyteStream> streamsForPkSync = new ArrayList<>();
    fullCatalog.getStreams().stream()
        .filter(stream -> streamsStillinPkSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .forEach(streamsForPkSync::add);
    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyStreamsToSnapshot(fullCatalog, stateManager.getInitialStreamsSynced());
    streamsForPkSync.addAll(newlyAddedStreams);

    return new InitialLoadStreams(streamsForPkSync, pairToInitialLoadStatus);
  }

  /**
   * Determines the streams to sync for initial primary key load. These include streams that are (i)
   * currently in primary key load (ii) newly added incremental streams.
   */
  public static InitialLoadStreams streamsForInitialPrimaryKeyLoad(final StateManager stateManager,
                                                                   final ConfiguredAirbyteCatalog fullCatalog) {

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

        final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
            streamDescriptor.getNamespace());

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
        .filter(stream -> streamsStillInPkSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .forEach(streamsForPkSync::add);

    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyStreamsToSnapshot(fullCatalog,
        Collections.unmodifiableSet(alreadySeenStreamPairs));
    streamsForPkSync.addAll(newlyAddedStreams);
    return new InitialLoadStreams(streamsForPkSync.stream().filter(MySqlInitialReadUtil::streamHasPrimaryKey).collect(Collectors.toList()),
        pairToInitialLoadStatus);
  }

  private static boolean streamHasPrimaryKey(final ConfiguredAirbyteStream stream) {
    return stream.getStream().getSourceDefinedPrimaryKey().size() > 0;
  }

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

  // Build a map of stream <-> primary key info (primary key field name + datatype) for all streams
  // currently undergoing initial primary key syncs.
  public static Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, PrimaryKeyInfo> initPairToPrimaryKeyInfoMap(
                                                                                                                           final JdbcDatabase database,
                                                                                                                           final InitialLoadStreams initialLoadStreams,
                                                                                                                           final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                                                                                                           final String quoteString) {
    final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPkInfoMap = new HashMap<>();
    // For every stream that is in primary initial key sync, we want to maintain information about the
    // current primary key info associated with the
    // stream
    initialLoadStreams.streamsForInitialLoad().forEach(stream -> {
      final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair =
          new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      final PrimaryKeyInfo pkInfo = getPrimaryKeyInfo(database, stream, tableNameToTable, quoteString);
      pairToPkInfoMap.put(pair, pkInfo);
    });
    return pairToPkInfoMap;
  }

  // Returns the primary key info associated with the stream.
  private static PrimaryKeyInfo getPrimaryKeyInfo(final JdbcDatabase database,
                                                  final ConfiguredAirbyteStream stream,
                                                  final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                                  final String quoteString) {
    // For cursor-based syncs, we cannot always assume a primary key field exists. We need to handle the
    // case where it does not exist when we support
    // cursor-based syncs.
    if (stream.getStream().getSourceDefinedPrimaryKey().size() > 1) {
      LOGGER.info("Composite primary key detected for {namespace, stream} : {}, {}", stream.getStream().getNamespace(), stream.getStream().getName());
    }
    final String pkFieldName = stream.getStream().getSourceDefinedPrimaryKey().get(0).get(0);
    final String fullyQualifiedTableName =
        DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getStream().getNamespace(), (stream.getStream().getName()));
    final TableInfo<CommonField<MysqlType>> table = tableNameToTable
        .get(fullyQualifiedTableName);
    final MysqlType pkFieldType = table.getFields().stream()
        .filter(field -> field.getName().equals(pkFieldName))
        .findFirst().get().getType();

    final String pkMaxValue = MySqlQueryUtils.getMaxPkValueForStream(database, stream, pkFieldName, quoteString);
    return new PrimaryKeyInfo(pkFieldName, pkFieldType, pkMaxValue);
  }

  public record InitialLoadStreams(List<ConfiguredAirbyteStream> streamsForInitialLoad,
                                   Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToInitialLoadStatus) {

  }

  public record CursorBasedStreams(List<ConfiguredAirbyteStream> streamsForCursorBased,
                                   Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus) {

  }

  public record PrimaryKeyInfo(String pkFieldName, MysqlType fieldType, String pkMaxValue) {}

  public static AirbyteStreamNameNamespacePair convertNameNamespacePairFromV0(final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair v1NameNamespacePair) {
    return new AirbyteStreamNameNamespacePair(v1NameNamespacePair.getName(), v1NameNamespacePair.getNamespace());
  }

}
