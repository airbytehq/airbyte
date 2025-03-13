/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import static io.airbyte.cdk.db.DbAnalyticsUtils.cdcCursorInvalidMessage;
import static io.airbyte.cdk.db.DbAnalyticsUtils.cdcResyncMessage;
import static io.airbyte.cdk.db.DbAnalyticsUtils.wassOccurrenceMessage;
import static io.airbyte.cdk.db.jdbc.JdbcUtils.getFullyQualifiedTableName;
import static io.airbyte.integrations.source.mssql.MsSqlSpecConstants.FAIL_SYNC_OPTION;
import static io.airbyte.integrations.source.mssql.MsSqlSpecConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.mssql.MsSqlSpecConstants.RESYNC_DATA_OPTION;
import static io.airbyte.integrations.source.mssql.MssqlCdcHelper.getDebeziumProperties;
import static io.airbyte.integrations.source.mssql.MssqlQueryUtils.getTableSizeInfoForStreams;
import static io.airbyte.integrations.source.mssql.cdc.MssqlCdcStateConstants.MSSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.ORDERED_COL_STATE_TYPE;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.STATE_TYPE_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Sets;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter;
import io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumEventConverter;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumPropertiesManager;
import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.InitialLoadTimeoutUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.models.CursorBasedStatus;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mssql.*;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil.MssqlDebeziumStateAttributes;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.*;
import io.debezium.connector.sqlserver.Lsn;
import java.sql.JDBCType;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlInitialReadUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlInitialReadUtil.class);
  private static final int MIN_QUEUE_SIZE = 1000;
  private static final int MAX_QUEUE_SIZE = 10000;

  public record InitialLoadStreams(List<ConfiguredAirbyteStream> streamsForInitialLoad,
                                   Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToInitialLoadStatus) {

  }

  public record CursorBasedStreams(List<ConfiguredAirbyteStream> streamsForCursorBased,
                                   Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus) {

  }

  public record OrderedColumnInfo(String ocFieldName, JDBCType fieldType, String ocMaxValue) {}

  public static Optional<MssqlInitialLoadHandler> getMssqlFullRefreshInitialLoadHandler(final JdbcDatabase database,
                                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                                        final MssqlInitialLoadStateManager initialLoadStateManager,
                                                                                        final StateManager stateManager,
                                                                                        final ConfiguredAirbyteStream fullRefreshStream,
                                                                                        final Instant emittedAt,
                                                                                        final String quoteString) {
    final boolean savedOffsetStillPresentOnServer = isSavedOffsetStillPresentOnServer(database, catalog, stateManager);
    final InitialLoadStreams initialLoadStreams =
        cdcStreamsForInitialOrderedColumnLoad(stateManager.getCdcStateManager(), catalog, savedOffsetStillPresentOnServer);

    // State manager will need to know all streams in order to produce a state message
    // But for initial load handler we only want to produce iterator on the single full refresh stream.
    if (!initialLoadStreams.streamsForInitialLoad().isEmpty()) {
      // Filter on initialLoadStream
      var pair = new AirbyteStreamNameNamespacePair(fullRefreshStream.getStream().getName(), fullRefreshStream.getStream().getNamespace());
      var ocStatus = initialLoadStreams.pairToInitialLoadStatus.get(pair);
      Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> fullRefreshOcStatus;
      if (ocStatus == null) {
        fullRefreshOcStatus = Map.of();
      } else {
        fullRefreshOcStatus = Map.of(pair, ocStatus);
      }

      var fullRefreshStreamInitialLoad = new InitialLoadStreams(List.of(fullRefreshStream), fullRefreshOcStatus);
      return Optional
          .of(getMssqlInitialLoadHandler(database, emittedAt, quoteString, fullRefreshStreamInitialLoad, initialLoadStateManager, Optional.empty()));
    }
    return Optional.empty();
  }

  private static MssqlInitialLoadHandler getMssqlInitialLoadHandler(final JdbcDatabase database,
                                                                    final Instant emittedAt,
                                                                    final String quoteString,
                                                                    final InitialLoadStreams initialLoadStreams,
                                                                    final MssqlInitialLoadStateManager initialLoadStateManager,
                                                                    final Optional<CdcMetadataInjector> metadataInjector) {
    final JsonNode sourceConfig = database.getSourceConfig();

    final MssqlSourceOperations sourceOperations = new MssqlSourceOperations(metadataInjector);

    return new MssqlInitialLoadHandler(sourceConfig, database,
        sourceOperations, quoteString, initialLoadStateManager,
        Optional.empty(),
        getTableSizeInfoForStreams(database, initialLoadStreams.streamsForInitialLoad(), quoteString));
  }

  private static CdcState getCdcState(final JdbcDatabase database,
                                      final ConfiguredAirbyteCatalog catalog,
                                      final StateManager stateManager,
                                      final boolean savedOffsetStillPresentOnServer) {
    if (!savedOffsetStillPresentOnServer || (stateManager.getCdcStateManager().getCdcState() == null
        || stateManager.getCdcStateManager().getCdcState().getState() == null)) {
      // Construct the initial state for Mssql. If there is already existing state, we use that instead
      // since that is associated with the debezium state associated with the initial sync.
      final JsonNode initialDebeziumState = MssqlDebeziumStateUtil.constructInitialDebeziumState(
          getDebeziumProperties(database, catalog, false), catalog, database);
      return new CdcState().withState(initialDebeziumState);
    } else {
      return stateManager.getCdcStateManager().getCdcState();
    }
  }

  public static boolean isSavedOffsetStillPresentOnServer(final JdbcDatabase database,
                                                          final ConfiguredAirbyteCatalog catalog,
                                                          final StateManager stateManager) {
    final MssqlDebeziumStateUtil mssqlDebeziumStateUtil = new MssqlDebeziumStateUtil();
    final JsonNode sourceConfig = database.getSourceConfig();

    final JsonNode state =
        (stateManager.getCdcStateManager().getCdcState() == null || stateManager.getCdcStateManager().getCdcState().getState() == null)
            ? MssqlDebeziumStateUtil.constructInitialDebeziumState(getDebeziumProperties(database, catalog, false), catalog, database)
            : Jsons.clone(stateManager.getCdcStateManager().getCdcState().getState());

    final Optional<MssqlDebeziumStateAttributes> savedOffset = mssqlDebeziumStateUtil.savedOffset(
        getDebeziumProperties(database, catalog, true), catalog, state.get(MSSQL_CDC_OFFSET), sourceConfig);

    final boolean savedOffsetStillPresentOnServer =
        savedOffset.isPresent() && mssqlDebeziumStateUtil.savedOffsetStillPresentOnServer(database, savedOffset.get());

    if (!savedOffsetStillPresentOnServer) {
      AirbyteTraceMessageUtility.emitAnalyticsTrace(cdcCursorInvalidMessage());
      if (!sourceConfig.get("replication_method").has(INVALID_CDC_CURSOR_POSITION_PROPERTY) || sourceConfig.get("replication_method").get(
          INVALID_CDC_CURSOR_POSITION_PROPERTY).asText().equals(FAIL_SYNC_OPTION)) {
        throw new ConfigErrorException(
            "Saved offset no longer present on the server. Please reset the connection, and then increase binlog retention and/or increase sync frequency.");
      } else if (sourceConfig.get("replication_method").get(INVALID_CDC_CURSOR_POSITION_PROPERTY).asText().equals(RESYNC_DATA_OPTION)) {
        AirbyteTraceMessageUtility.emitAnalyticsTrace(cdcResyncMessage());
        LOGGER.warn("Saved offset no longer present on the server, Airbyte is going to trigger a sync from scratch");
      }
    }
    return savedOffsetStillPresentOnServer;
  }

  public static MssqlInitialLoadGlobalStateManager getMssqlInitialLoadGlobalStateManager(final JdbcDatabase database,
                                                                                         final ConfiguredAirbyteCatalog catalog,
                                                                                         final StateManager stateManager,
                                                                                         final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                                         final String quoteString) {
    final boolean savedOffsetStillPresentOnServer = isSavedOffsetStillPresentOnServer(database, catalog, stateManager);
    final InitialLoadStreams initialLoadStreams =
        cdcStreamsForInitialOrderedColumnLoad(stateManager.getCdcStateManager(), catalog, savedOffsetStillPresentOnServer);
    final CdcState initialStateToBeUsed = getCdcState(database, catalog, stateManager, savedOffsetStillPresentOnServer);

    return new MssqlInitialLoadGlobalStateManager(initialLoadStreams,
        initPairToOrderedColumnInfoMap(database, catalog, tableNameToTable, quoteString),
        stateManager, catalog, initialStateToBeUsed);
  }

  public static List<AutoCloseableIterator<AirbyteMessage>> getCdcReadIterators(final JdbcDatabase database,
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                                final StateManager stateManager,
                                                                                final MssqlInitialLoadStateManager initialLoadStateManager,
                                                                                final Instant emittedAt,
                                                                                final String quoteString) {
    final JsonNode sourceConfig = database.getSourceConfig();
    final Duration firstRecordWaitTime = RecordWaitTimeUtil.getFirstRecordWaitTime(sourceConfig);
    LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
    final int queueSize = getQueueSize(sourceConfig);
    LOGGER.info("Queue size: {}", queueSize);
    final Duration initialLoadTimeout = InitialLoadTimeoutUtil.getInitialLoadTimeout(sourceConfig);
    // Determine the streams that need to be loaded via primary key sync.
    final List<AutoCloseableIterator<AirbyteMessage>> initialLoadIterator = new ArrayList<>();
    final boolean savedOffsetStillPresentOnServer = isSavedOffsetStillPresentOnServer(database, catalog, stateManager);
    final InitialLoadStreams initialLoadStreams =
        cdcStreamsForInitialOrderedColumnLoad(stateManager.getCdcStateManager(), catalog, savedOffsetStillPresentOnServer);
    final MssqlCdcConnectorMetadataInjector metadataInjector = MssqlCdcConnectorMetadataInjector.getInstance(emittedAt);
    final CdcState stateToBeUsed = getCdcState(database, catalog, stateManager, savedOffsetStillPresentOnServer);

    // Debezium is started for streams that have been started - that is they have been partially or
    // fully completed.
    final var startedCdcStreamList = catalog.getStreams().stream()
        .filter(stream -> stream.getSyncMode() == SyncMode.INCREMENTAL)
        .filter(stream -> isStreamPartiallyOrFullyCompleted(stream, initialLoadStreams))
        .map(stream -> stream.getStream().getNamespace() + "." + stream.getStream().getName()).toList();

    final var allCdcStreamList = catalog.getStreams().stream()
        .filter(stream -> stream.getSyncMode() == SyncMode.INCREMENTAL)
        .map(stream -> stream.getStream().getNamespace() + "." + stream.getStream().getName()).toList();

    // If there are streams to sync via ordered column load, build the relevant iterators.
    if (!initialLoadStreams.streamsForInitialLoad().isEmpty()) {
      final MssqlDebeziumStateAttributes stateAttributes = MssqlDebeziumStateUtil.getStateAttributesFromDB(database);
      final MssqlInitialLoadHandler initialLoadHandler =
          getMssqlInitialLoadHandler(database, emittedAt, quoteString, initialLoadStreams, initialLoadStateManager,
              Optional.of(new CdcMetadataInjector(emittedAt.toString(), stateAttributes, metadataInjector)));
      // Because initial load streams will be followed by cdc read of those stream, we only decorate with
      // complete status trace after CDC read is done.
      initialLoadIterator.addAll(initialLoadHandler.getIncrementalIterators(
          new ConfiguredAirbyteCatalog().withStreams(initialLoadStreams.streamsForInitialLoad()),
          tableNameToTable,
          emittedAt, false, false, Optional.empty()));
    }

    final List<AutoCloseableIterator<AirbyteMessage>> cdcStreamsStartStatusEmitters = catalog.getStreams().stream()
        .filter(stream -> stream.getSyncMode() == SyncMode.INCREMENTAL)
        .map(stream -> (AutoCloseableIterator<AirbyteMessage>) new StreamStatusTraceEmitterIterator(
            new AirbyteStreamStatusHolder(
                new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace()),
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED)))
        .toList();

    final List<AutoCloseableIterator<AirbyteMessage>> cdcStreamsEndStatusEmitters = catalog.getStreams().stream()
        .filter(stream -> stream.getSyncMode() == SyncMode.INCREMENTAL)
        .map(stream -> (AutoCloseableIterator<AirbyteMessage>) new StreamStatusTraceEmitterIterator(
            new AirbyteStreamStatusHolder(
                new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace()),
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)))
        .toList();

    // Build the incremental CDC iterators.
    final var targetPosition = MssqlCdcTargetPosition.getTargetPosition(database, sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());
    final AirbyteDebeziumHandler<Lsn> handler = new AirbyteDebeziumHandler<>(
        sourceConfig,
        targetPosition,
        true,
        firstRecordWaitTime,
        queueSize,
        false);

    final var eventConverter = new RelationalDbDebeziumEventConverter(metadataInjector, emittedAt);

    if (startedCdcStreamList.isEmpty()) {
      LOGGER.info("First sync - no cdc streams have been completed or started");
      /*
       * This is the first run case - no initial loads have been started. In this case, we want to run the
       * iterators in the following order: 1. Run the initial load iterators. This step will timeout and
       * throw a transient error if run for too long (> 8hrs by default). 2. Run the debezium iterators
       * with ALL of the incremental streams configured. This is because if step 1 completes, the initial
       * load can be considered finished.
       */
      final var propertiesManager =
          new RelationalDbDebeziumPropertiesManager(getDebeziumProperties(database, catalog, false), sourceConfig, catalog, allCdcStreamList);
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorsSupplier = getCdcIncrementalIteratorsSupplier(handler,
          propertiesManager, eventConverter, stateToBeUsed, stateManager);
      return Collections.singletonList(
          AutoCloseableIterators.concatWithEagerClose(
              Stream
                  .of(
                      cdcStreamsStartStatusEmitters,
                      initialLoadIterator,
                      Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorsSupplier, null)),
                      cdcStreamsEndStatusEmitters)
                  .flatMap(Collection::stream)
                  .collect(Collectors.toList()),
              AirbyteTraceMessageUtility::emitStreamStatusTrace));
    } else if (initialLoadIterator.isEmpty()) {
      LOGGER.info("Initial load has finished completely - only reading the binlog");
      /*
       * In this case, the initial load has completed and only debezium should be run. The iterators
       * should be run in the following order: 1. Run the debezium iterators with ALL of the incremental
       * streams configured.
       */
      final var propertiesManager =
          new RelationalDbDebeziumPropertiesManager(getDebeziumProperties(database, catalog, false), sourceConfig, catalog, allCdcStreamList);
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = getCdcIncrementalIteratorsSupplier(handler,
          propertiesManager, eventConverter, stateToBeUsed, stateManager);
      return Collections.singletonList(
          AutoCloseableIterators.concatWithEagerClose(
              Stream
                  .of(
                      cdcStreamsStartStatusEmitters,
                      Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)),
                      cdcStreamsEndStatusEmitters)
                  .flatMap(Collection::stream)
                  .collect(Collectors.toList()),
              AirbyteTraceMessageUtility::emitStreamStatusTrace));
    } else {
      LOGGER.info("Initial load is in progress - reading binlog first and then resuming with initial load.");
      /*
       * In this case, the initial load has partially completed (WASS case). The iterators should be run
       * in the following order: 1. Run the debezium iterators with only the incremental streams which
       * have been fully or partially completed configured. 2. Resume initial load for partially completed
       * and not started streams. This step will timeout and throw a transient error if run for too long
       * (> 8hrs by default).
       */
      AirbyteTraceMessageUtility.emitAnalyticsTrace(wassOccurrenceMessage());
      final var propertiesManager =
          new RelationalDbDebeziumPropertiesManager(getDebeziumProperties(database, catalog, false), sourceConfig, catalog, startedCdcStreamList);
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = getCdcIncrementalIteratorsSupplier(handler,
          propertiesManager, eventConverter, stateToBeUsed, stateManager);
      return Collections.singletonList(
          AutoCloseableIterators.concatWithEagerClose(
              Stream
                  .of(
                      cdcStreamsStartStatusEmitters,
                      Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)),
                      initialLoadIterator,
                      cdcStreamsEndStatusEmitters)
                  .flatMap(Collection::stream)
                  .collect(Collectors.toList()),
              AirbyteTraceMessageUtility::emitStreamStatusTrace));
    }
  }

  public static InitialLoadStreams cdcStreamsForInitialOrderedColumnLoad(final CdcStateManager stateManager,
                                                                         final ConfiguredAirbyteCatalog fullCatalog,
                                                                         final boolean savedOffsetStillPresentOnServer) {
    if (!savedOffsetStillPresentOnServer) {
      // Add a filter here to identify resumable full refresh streams.
      return new InitialLoadStreams(
          fullCatalog.getStreams()
              .stream()
              .collect(Collectors.toList()),
          new HashMap<>());
    }
    final AirbyteStateMessage airbyteStateMessage = stateManager.getRawStateMessage();
    final Set<AirbyteStreamNameNamespacePair> streamsStillInOcSync = new HashSet<>();

    // Build a map of stream <-> initial load status for streams that currently have an initial primary
    // key load in progress.
    final Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToInitialLoadStatus = new HashMap<>();
    if (airbyteStateMessage != null && airbyteStateMessage.getGlobal() != null && airbyteStateMessage.getGlobal().getStreamStates() != null) {
      LOGGER.info("Trying to extract streams need initial oc sync. State message: {}", airbyteStateMessage);
      airbyteStateMessage.getGlobal().getStreamStates().forEach(stateMessage -> {
        LOGGER.info("State message in this stream: {}", stateMessage);
        final JsonNode streamState = stateMessage.getStreamState();
        final StreamDescriptor streamDescriptor = stateMessage.getStreamDescriptor();
        if (streamState == null || streamDescriptor == null) {
          return;
        }

        if (streamState.has(STATE_TYPE_KEY)) {
          if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(ORDERED_COL_STATE_TYPE)) {
            final OrderedColumnLoadStatus orderedColumnLoadStatus = Jsons.object(streamState, OrderedColumnLoadStatus.class);
            final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(),
                streamDescriptor.getNamespace());
            pairToInitialLoadStatus.put(pair, orderedColumnLoadStatus);
            streamsStillInOcSync.add(pair);
          }
        }
      });
    }

    final List<ConfiguredAirbyteStream> streamForOcSync = new ArrayList<>();
    fullCatalog.getStreams().stream()
        .filter(stream -> streamsStillInOcSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .forEach(streamForOcSync::add);
    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyStreamsToSnapshot(fullCatalog, stateManager.getInitialStreamsSynced());
    streamForOcSync.addAll(newlyAddedStreams);

    return new InitialLoadStreams(streamForOcSync, pairToInitialLoadStatus);
  }

  public static Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> initPairToOrderedColumnInfoMap(
                                                                                                      final JdbcDatabase database,
                                                                                                      final ConfiguredAirbyteCatalog catalog,
                                                                                                      final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                                                      final String quoteString) {
    final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOcInfoMap = new HashMap<>();
    // For every stream that is in initial ordered column sync, we want to maintain information about
    // the current ordered column info associated with the stream
    catalog.getStreams().forEach(stream -> {
      final AirbyteStreamNameNamespacePair pair =
          new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      final Optional<OrderedColumnInfo> ocInfo = getOrderedColumnInfo(database, stream, tableNameToTable, quoteString);
      if (ocInfo.isPresent()) {
        pairToOcInfoMap.put(pair, ocInfo.get());
      }
    });
    return pairToOcInfoMap;
  }

  static Optional<OrderedColumnInfo> getOrderedColumnInfo(final JdbcDatabase database,
                                                          final ConfiguredAirbyteStream stream,
                                                          final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                          final String quoteString) {
    final String fullyQualifiedTableName =
        DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getStream().getNamespace(), stream.getStream().getName());
    final TableInfo<CommonField<JDBCType>> table = tableNameToTable
        .get(fullyQualifiedTableName);
    return getOrderedColumnInfo(database, stream, table, quoteString);
  }

  static Optional<OrderedColumnInfo> getOrderedColumnInfo(final JdbcDatabase database,
                                                          final ConfiguredAirbyteStream stream,
                                                          final TableInfo<CommonField<JDBCType>> table,
                                                          final String quoteString) {
    // For cursor-based syncs, we cannot always assume a ordered column field exists. We need to handle
    // the case where it does not exist when we support cursor-based syncs.
    // if (stream.getStream().getSourceDefinedPrimaryKey().size() > 1) {
    // LOGGER.info("Composite primary key detected for {namespace, stream} : {}, {}",
    // stream.getStream().getNamespace(), stream.getStream().getName());
    // }
    Optional<String> ocFieldNameOpt = selectOcFieldName(database, stream);
    if (ocFieldNameOpt.isEmpty()) {
      LOGGER.info("No primary key or clustered index found for stream: " + stream.getStream().getName());
      return Optional.empty();
    }

    String ocFieldName = ocFieldNameOpt.get();
    LOGGER.info("selected ordered column field name: " + ocFieldName);
    final JDBCType ocFieldType = table.getFields().stream()
        .filter(field -> field.getName().equals(ocFieldName))
        .findFirst().get().getType();
    final String ocMaxValue = MssqlQueryUtils.getMaxOcValueForStream(database, stream, ocFieldName, quoteString);
    return Optional.of(new OrderedColumnInfo(ocFieldName, ocFieldType, ocMaxValue));
  }

  @VisibleForTesting
  public static Optional<String> selectOcFieldName(final JdbcDatabase database,
                                                   final ConfiguredAirbyteStream stream) {

    final Map<String, List<String>> clusterdIndexField = MssqlInitialLoadHandler.discoverClusteredIndexForStream(database, stream.getStream());
    final String streamName = getFullyQualifiedTableName(stream.getStream().getNamespace(), stream.getStream().getName());
    final List<List<String>> primaryKey = stream.getStream().getSourceDefinedPrimaryKey();
    final String ocFieldName;

    final List<String> clusterColumns = Optional.ofNullable(clusterdIndexField)
        .map(map -> map.get(streamName))
        .orElse(new ArrayList<>());

    // Use the clustered index unless it is composite. Otherwise, default to the primary key.
    if (clusterColumns.size() == 1) {
      ocFieldName = clusterColumns.getFirst();
    } else if (!primaryKey.isEmpty()) {
      LOGGER.info("Clustered index is empty or composite. Defaulting to primary key.");
      ocFieldName = primaryKey.getFirst().getFirst();
    } else {
      return Optional.empty();
    }
    return Optional.of(ocFieldName);
  }

  public static List<ConfiguredAirbyteStream> identifyStreamsToSnapshot(final ConfiguredAirbyteCatalog catalog,
                                                                        final Set<AirbyteStreamNameNamespacePair> alreadySyncedStreams) {
    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(Sets.difference(allStreams, alreadySyncedStreams));
    // Add a filter here to identify resumable full refresh streams.
    return catalog.getStreams().stream()
        .filter(stream -> newlyAddedStreams.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
  }

  public static InitialLoadStreams streamsForInitialOrderedColumnLoad(final StateManager stateManager,
                                                                      final ConfiguredAirbyteCatalog fullCatalog) {

    final List<AirbyteStateMessage> rawStateMessages = stateManager.getRawStateMessages();
    final Set<AirbyteStreamNameNamespacePair> streamsStillInOrderedColumnSync = new HashSet<>();
    final Set<AirbyteStreamNameNamespacePair> alreadySeenStreamPairs = new HashSet<>();

    // Build a map of stream <-> initial load status for streams that currently have an initial primary
    // key load in progress.
    final Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToInitialLoadStatus = new HashMap<>();
    LOGGER.info("raw state message: " + rawStateMessages);
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
          if (streamState.get(STATE_TYPE_KEY).asText().equalsIgnoreCase(ORDERED_COL_STATE_TYPE)) {
            final OrderedColumnLoadStatus orderedColumnLoadStatus = Jsons.object(streamState, OrderedColumnLoadStatus.class);
            pairToInitialLoadStatus.put(pair, orderedColumnLoadStatus);
            streamsStillInOrderedColumnSync.add(pair);
          }
        }
        alreadySeenStreamPairs.add(new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace()));
      });
    }
    final List<ConfiguredAirbyteStream> streamsForOcSync = new ArrayList<>();
    LOGGER.info("alreadySeenStreamPairs: {}", alreadySeenStreamPairs);
    fullCatalog.getStreams().stream()
        .filter(stream -> streamsStillInOrderedColumnSync.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .forEach(streamsForOcSync::add);

    final List<ConfiguredAirbyteStream> newlyAddedStreams = identifyStreamsToSnapshot(fullCatalog,
        Collections.unmodifiableSet(alreadySeenStreamPairs));
    streamsForOcSync.addAll(newlyAddedStreams);
    LOGGER.info("streamsForOcSync: {}", streamsForOcSync);
    return new InitialLoadStreams(streamsForOcSync.stream().filter((stream) -> !stream.getStream().getSourceDefinedPrimaryKey()
        .isEmpty()).collect(Collectors.toList()),
        pairToInitialLoadStatus);
  }

  private static OptionalInt extractQueueSizeFromConfig(final JsonNode config) {
    final JsonNode replicationMethod = config.get("replication_method");
    if (replicationMethod != null && replicationMethod.has("queue_size")) {
      final int queueSize = config.get("replication_method").get("queue_size").asInt();
      return OptionalInt.of(queueSize);
    }
    return OptionalInt.empty();
  }

  @SuppressWarnings("unchecked")
  private static Supplier<AutoCloseableIterator<AirbyteMessage>> getCdcIncrementalIteratorsSupplier(AirbyteDebeziumHandler handler,
                                                                                                    RelationalDbDebeziumPropertiesManager propertiesManager,
                                                                                                    DebeziumEventConverter eventConverter,
                                                                                                    CdcState stateToBeUsed,
                                                                                                    StateManager stateManager) {
    return () -> handler.getIncrementalIterators(
        propertiesManager, eventConverter, new MssqlCdcSavedInfoFetcher(stateToBeUsed), new MssqlCdcStateHandler(stateManager));
  }

  private static boolean isStreamPartiallyOrFullyCompleted(ConfiguredAirbyteStream stream, InitialLoadStreams initialLoadStreams) {
    boolean isStreamCompleted = !initialLoadStreams.streamsForInitialLoad.contains(stream);
    // A stream has been partially completed if an initial load status exists.
    boolean isStreamPartiallyCompleted = (initialLoadStreams.pairToInitialLoadStatus
        .get(new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace()))) != null;
    return isStreamCompleted || isStreamPartiallyCompleted;
  }

  public static int getQueueSize(final JsonNode config) {
    final OptionalInt sizeFromConfig = extractQueueSizeFromConfig(config);
    if (sizeFromConfig.isPresent()) {
      final int size = sizeFromConfig.getAsInt();
      if (size < MIN_QUEUE_SIZE) {
        LOGGER.warn("Queue size is overridden to {} , which is the min allowed for safety.",
            MIN_QUEUE_SIZE);
        return MIN_QUEUE_SIZE;
      } else if (size > MAX_QUEUE_SIZE) {
        LOGGER.warn("Queue size is overridden to {} , which is the max allowed for safety.",
            MAX_QUEUE_SIZE);
        return MAX_QUEUE_SIZE;
      }
      return size;
    }
    return MAX_QUEUE_SIZE;
  }

  public static InitialLoadStreams filterStreamInIncrementalMode(final InitialLoadStreams stream) {
    return new InitialLoadStreams(
        stream.streamsForInitialLoad.stream().filter(airbyteStream -> airbyteStream.getSyncMode() == SyncMode.INCREMENTAL)
            .collect(Collectors.toList()),
        stream.pairToInitialLoadStatus);
  }

}
