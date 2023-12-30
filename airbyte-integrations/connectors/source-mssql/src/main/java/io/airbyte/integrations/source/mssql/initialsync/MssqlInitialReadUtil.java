/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import static io.airbyte.integrations.source.mssql.MssqlCdcHelper.getDebeziumProperties;
import static io.airbyte.integrations.source.mssql.MssqlQueryUtils.getTableSizeInfoForStreams;
import static io.airbyte.integrations.source.mssql.MssqlQueryUtils.prettyPrintConfiguredAirbyteStreamList;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.ORDERED_COL_STATE_TYPE;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.STATE_TYPE_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Sets;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager.DebeziumConnectorType;
import io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil;
import io.airbyte.cdk.integrations.debezium.internals.mssql.MssqlDebeziumStateUtil;
import io.airbyte.cdk.integrations.debezium.internals.mssql.MssqlDebeziumStateUtil.MssqlDebeziumStateAttributes;
import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mssql.MssqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mssql.MssqlCdcSavedInfoFetcher;
import io.airbyte.integrations.source.mssql.MssqlCdcStateHandler;
import io.airbyte.integrations.source.mssql.MssqlCdcTargetPosition;
import io.airbyte.integrations.source.mssql.MssqlQueryUtils;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.sqlserver.Lsn;
import java.sql.JDBCType;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlInitialReadUtil {
  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlInitialReadUtil.class);

  public record InitialLoadStreams(List<ConfiguredAirbyteStream> streamsForInitialLoad,
                                   Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToInitialLoadStatus) {

  }

  public record OrderedColumnInfo(String ocFieldName, JDBCType fieldType, String ocMaxValue) {}

  public static List<AutoCloseableIterator<AirbyteMessage>> getCdcReadIterators(final JdbcDatabase database,
      final ConfiguredAirbyteCatalog catalog,
      final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
      final StateManager stateManager,
      final Instant emittedAt,
      final String quoteString) {
    final JsonNode sourceConfig = database.getSourceConfig();
    final Duration firstRecordWaitTime = RecordWaitTimeUtil.getFirstRecordWaitTime(sourceConfig);
    final Duration subsequentRecordWaitTime = RecordWaitTimeUtil.getSubsequentRecordWaitTime(sourceConfig);
    LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
    // Determine the streams that need to be loaded via primary key sync.
    final List<AutoCloseableIterator<AirbyteMessage>> initialLoadIterator = new ArrayList<>();
    // Construct the initial state for Mssql. If there is already existing state, we use that instead
    // since that is associated with the debezium
    // state associated with the initial sync.
    final MssqlDebeziumStateUtil mssqlDebeziumStateUtil = new MssqlDebeziumStateUtil();
    final JsonNode initialDebeziumState = mssqlDebeziumStateUtil.constructInitialDebeziumState(
        getDebeziumProperties(database, catalog, false), catalog, database);

    final JsonNode state =
        (stateManager.getCdcStateManager().getCdcState() == null || stateManager.getCdcStateManager().getCdcState().getState() == null)
            ? initialDebeziumState
            : Jsons.clone(stateManager.getCdcStateManager().getCdcState().getState());

/*
    final Optional<MysqlDebeziumStateAttributes> savedOffset = mySqlDebeziumStateUtil.savedOffset(
        MySqlCdcProperties.getDebeziumProperties(database), catalog, state.get(MYSQL_CDC_OFFSET), sourceConfig);

    final boolean savedOffsetStillPresentOnServer =
        savedOffset.isPresent() && mySqlDebeziumStateUtil.savedOffsetStillPresentOnServer(database, savedOffset.get());

    if (!savedOffsetStillPresentOnServer) {
      LOGGER.warn("Saved offset no longer present on the server, Airbyte is going to trigger a sync from scratch");
    }

*/
    final boolean savedOffsetStillPresentOnServer = true; // TEMP
    final InitialLoadStreams initialLoadStreams = cdcStreamsForInitialOrderedCoumnLoad(stateManager.getCdcStateManager(), catalog, savedOffsetStillPresentOnServer);
    final CdcState stateToBeUsed = (!savedOffsetStillPresentOnServer || (stateManager.getCdcStateManager().getCdcState() == null
        || stateManager.getCdcStateManager().getCdcState().getState() == null)) ? new CdcState().withState(initialDebeziumState)
        : stateManager.getCdcStateManager().getCdcState();

    final MssqlCdcConnectorMetadataInjector mssqlCdcConnectorMetadataInjector = MssqlCdcConnectorMetadataInjector.getInstance(emittedAt);
    // If there are streams to sync via ordered column load, build the relevant iterators.
    if (!initialLoadStreams.streamsForInitialLoad().isEmpty()) {
      LOGGER.info("Streams to be synced via ordered column : {}", initialLoadStreams.streamsForInitialLoad().size());
      LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(initialLoadStreams.streamsForInitialLoad()));
      final MssqlInitialLoadStateManager initialLoadStateManager =
          new MssqlInitialLoadGlobalStateManager(initialLoadStreams,
              initPairToOrderedColumnInfoMap(database, initialLoadStreams, tableNameToTable, quoteString),
              stateToBeUsed, catalog);
      final MssqlDebeziumStateAttributes stateAttributes = MssqlDebeziumStateUtil.getStateAttributesFromDB(database);

      final MssqlInitialLoadSourceOperations sourceOperations =
          new MssqlInitialLoadSourceOperations();

      final MssqlInitialLoadHandler initialLoadHandler = new MssqlInitialLoadHandler(sourceConfig, database,
          sourceOperations, quoteString, initialLoadStateManager,
          namespacePair -> Jsons.emptyObject(),
          getTableSizeInfoForStreams(database, initialLoadStreams.streamsForInitialLoad(), quoteString));

      initialLoadIterator.addAll(initialLoadHandler.getIncrementalIterators(
          new ConfiguredAirbyteCatalog().withStreams(initialLoadStreams.streamsForInitialLoad()),
          tableNameToTable,
          emittedAt));
    } else {
      LOGGER.info("No streams will be synced via ordered column");
    }

    // Build the incremental CDC iterators.
    final var targetPosition = MssqlCdcTargetPosition.getTargetPosition(database, sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());
    final AirbyteDebeziumHandler<Lsn> handler = new AirbyteDebeziumHandler<>(
        sourceConfig,
        targetPosition,
        true,
        firstRecordWaitTime,
        subsequentRecordWaitTime,
        OptionalInt.empty());

    final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorsSupplier = () -> handler.getIncrementalIterators(catalog,
        new MssqlCdcSavedInfoFetcher(stateToBeUsed),
        new MssqlCdcStateHandler(stateManager),
        mssqlCdcConnectorMetadataInjector,
        getDebeziumProperties(database, catalog, false),
        DebeziumConnectorType.RELATIONALDB,
        emittedAt,
        true); // TODO: check why add db name to state

    // This starts processing the transaction logs as soon as initial sync is complete, this is a bit
    // different
    // from the current cdc syncs.
    // We finish the current CDC once the initial snapshot is complete and the next sync starts
    // processing the transaction logs
    return Collections.singletonList(
        AutoCloseableIterators.concatWithEagerClose(
            Stream
                .of(initialLoadIterator, Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorsSupplier, null)))
                .flatMap(Collection::stream)
                .collect(Collectors.toList()),
            AirbyteTraceMessageUtility::emitStreamStatusTrace));
  }

  public static InitialLoadStreams cdcStreamsForInitialOrderedCoumnLoad(final CdcStateManager stateManager,
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
    final Set<AirbyteStreamNameNamespacePair> streamsStillInOcSync = new HashSet<>();

    // Build a map of stream <-> initial load status for streams that currently have an initial primary
    // key load in progress.
    final Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToInitialLoadStatus = new HashMap<>();
    if (airbyteStateMessage != null && airbyteStateMessage.getGlobal() != null && airbyteStateMessage.getGlobal().getStreamStates() != null) {
      airbyteStateMessage.getGlobal().getStreamStates().forEach(stateMessage -> {
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

  public static Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, OrderedColumnInfo> initPairToOrderedColumnInfoMap(
                                                                                                                                 final JdbcDatabase database,
                                                                                                                                 final InitialLoadStreams initialLoadStreams,
                                                                                                                                 final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                                                                                 final String quoteString) {
    final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOcInfoMap = new HashMap<>();
    // For every stream that is in initial ordered column sync, we want to maintain information about
    // the
    // current ordered column info associated with the
    // stream
    initialLoadStreams.streamsForInitialLoad.forEach(stream -> {
      final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair =
          new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      final OrderedColumnInfo ocInfo = getOrderedColumnInfo(database, stream, tableNameToTable, quoteString);
      pairToOcInfoMap.put(pair, ocInfo);
    });
    return pairToOcInfoMap;
  }

  final static OrderedColumnInfo getOrderedColumnInfo(final JdbcDatabase database,
                                                      final ConfiguredAirbyteStream stream,
                                                      final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                      final String quoteString) {
    // For cursor-based syncs, we cannot always assume a ordered column field exists. We need to handle
    // the
    // case where it does not exist when we support
    // cursor-based syncs.
    if (stream.getStream().getSourceDefinedPrimaryKey().size() > 1) { // TODO: validate the seleted column rather than primary key
      LOGGER.info("Composite primary key detected for {namespace, stream} : {}, {}", stream.getStream().getNamespace(), stream.getStream().getName());
    }
    final String ocFieldName = stream.getStream().getSourceDefinedPrimaryKey().get(0).get(0);
    final String fullyQualifiedTableName =
        DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getStream().getNamespace(), stream.getStream().getName());
    final TableInfo<CommonField<JDBCType>> table = tableNameToTable
        .get(fullyQualifiedTableName);
    final JDBCType ocFieldType = table.getFields().stream()
        .filter(field -> field.getName().equals(ocFieldName))
        .findFirst().get().getType();

    final String ocMaxValue = MssqlQueryUtils.getMaxOcValueForStream(database, stream, ocFieldName, quoteString);
    return new OrderedColumnInfo(ocFieldName, ocFieldType, ocMaxValue);
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
}
