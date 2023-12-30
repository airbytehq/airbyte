package io.airbyte.integrations.source.mssql.initialsync;

import static io.airbyte.integrations.source.mssql.MssqlCdcHelper.*;
import static io.airbyte.integrations.source.mssql.MssqlQueryUtils.prettyPrintConfiguredAirbyteStreamList;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager.DebeziumConnectorType;
import io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil;
import io.airbyte.cdk.integrations.debezium.internals.mssql.MssqlDebeziumStateUtil;
import io.airbyte.cdk.integrations.debezium.internals.mssql.MssqlDebeziumStateUtil.MssqlDebeziumStateAttributes;
import io.airbyte.cdk.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mssql.MssqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mssql.MssqlCdcHelper;
import io.airbyte.integrations.source.mssql.MssqlCdcSavedInfoFetcher;
import io.airbyte.integrations.source.mssql.MssqlCdcStateHandler;
import io.airbyte.integrations.source.mssql.MssqlCdcTargetPosition;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.debezium.connector.sqlserver.Lsn;
import java.sql.JDBCType;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.function.Supplier;
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
          namespacePair -> Jsons.emptyObject()); // TODO: add table size?

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
    true); // TODO: check why add db name to stete



    // Determine if new stream(s) have been added to the catalog after initial sync of existing streams
    final List<ConfiguredAirbyteStream> streamsToSnapshot = identifyStreamsToSnapshot(catalog, stateManager);
    final ConfiguredAirbyteCatalog streamsToSnapshotCatalog = new ConfiguredAirbyteCatalog().withStreams(streamsToSnapshot);

    final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorsSupplier = () -> handler.getIncrementalIterators(
        catalog,
        new MssqlCdcSavedInfoFetcher(stateManager.getCdcStateManager().getCdcState()),
        new MssqlCdcStateHandler(stateManager),
        mssqlCdcConnectorMetadataInjector,
        getDebeziumProperties(database, catalog, false),
        DebeziumPropertiesManager.DebeziumConnectorType.RELATIONALDB,
        emittedAt,
        true);

    /*
     * If the CDC state is null or there is no streams to snapshot, that means no stream has gone
     * through the initial sync, so we return the list of incremental iterators
     */
    if ((stateManager.getCdcStateManager().getCdcState() == null ||
        stateManager.getCdcStateManager().getCdcState().getState() == null ||
        streamsToSnapshot.isEmpty())) {
      return List.of(incrementalIteratorsSupplier.get());
    }

    // Otherwise, we build the snapshot iterators for the newly added streams(s)
    final AutoCloseableIterator<AirbyteMessage> snapshotIterators =
        handler.getSnapshotIterators(streamsToSnapshotCatalog,
            mssqlCdcConnectorMetadataInjector,
            getDebeziumProperties(database, catalog, true),
            new MssqlCdcStateHandler(stateManager),
            DebeziumPropertiesManager.DebeziumConnectorType.RELATIONALDB,
            emittedAt);
    /*
     * The incremental iterators needs to be wrapped in a lazy iterator since only 1 Debezium engine for
     * the DB can be running at a time
     */
    return List.of(snapshotIterators, AutoCloseableIterators.lazyIterator(incrementalIteratorsSupplier, null));
  }

  public static InitialLoadStreams cdcStreamsForInitialOrderedCoumnLoad(final CdcStateManager stateManager,
      final ConfiguredAirbyteCatalog fullCatalog,
      final boolean savedOffsetStillPresentOnServer) {

  }

  public static Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, OrderedColumnInfo> initPairToOrderedColumnInfoMap(
      final JdbcDatabase database,
      final InitialLoadStreams initialLoadStreams,
      final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
      final String quoteString) {

  }
}
