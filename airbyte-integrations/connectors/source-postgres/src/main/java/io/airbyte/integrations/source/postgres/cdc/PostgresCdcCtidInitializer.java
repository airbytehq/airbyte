/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.airbyte.cdk.db.DbAnalyticsUtils.cdcCursorInvalidMessage;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.streamsUnderVacuum;
import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.FAIL_SYNC_OPTION;
import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.postgres.PostgresUtils.isDebugMode;
import static io.airbyte.integrations.source.postgres.PostgresUtils.prettyPrintConfiguredAirbyteStreamList;
import static io.airbyte.integrations.source.postgres.ctid.CtidUtils.createInitialLoader;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumEventConverter;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumPropertiesManager;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils;
import io.airbyte.integrations.source.postgres.PostgresType;
import io.airbyte.integrations.source.postgres.PostgresUtils;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcCtidUtils.CtidStreams;
import io.airbyte.integrations.source.postgres.ctid.CtidGlobalStateManager;
import io.airbyte.integrations.source.postgres.ctid.FileNodeHandler;
import io.airbyte.integrations.source.postgres.ctid.PostgresCtidHandler;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCdcCtidInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcCtidInitializer.class);

  public static boolean getSavedOffsetAfterReplicationSlotLSN(final JdbcDatabase database,
                                                              final ConfiguredAirbyteCatalog catalog,
                                                              final StateManager stateManager,
                                                              final JsonNode replicationSlot) {
    final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();

    final CdcState defaultCdcState = getDefaultCdcState(postgresDebeziumStateUtil, database);

    final JsonNode state =
        (stateManager.getCdcStateManager().getCdcState() == null || stateManager.getCdcStateManager().getCdcState().getState() == null)
            ? defaultCdcState.getState()
            : Jsons.clone(stateManager.getCdcStateManager().getCdcState().getState());

    final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(
        Jsons.clone(PostgresCdcProperties.getDebeziumDefaultProperties(database)),
        catalog,
        state,
        database.getSourceConfig());
    return postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(
        // We can assume that there will be only 1 replication slot cause before the sync starts for
        // Postgres CDC,
        // we run all the check operations and one of the check validates that the replication slot exists
        // and has only 1 entry
        replicationSlot,
        savedOffset);
  }

  public static CtidGlobalStateManager getCtidInitialLoadGlobalStateManager(final JdbcDatabase database,
                                                                            final ConfiguredAirbyteCatalog catalog,
                                                                            final StateManager stateManager,
                                                                            final String quoteString,
                                                                            final boolean savedOffsetAfterReplicationSlotLSN) {
    final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();

    final CtidStreams ctidStreams = PostgresCdcCtidUtils.streamsToSyncViaCtid(stateManager.getCdcStateManager(), catalog,
        savedOffsetAfterReplicationSlotLSN);
    final List<AirbyteStreamNameNamespacePair> streamsUnderVacuum = new ArrayList<>();
    streamsUnderVacuum.addAll(streamsUnderVacuum(database,
        ctidStreams.streamsForCtidSync(), quoteString).result());

    final List<ConfiguredAirbyteStream> finalListOfStreamsToBeSyncedViaCtid =
        streamsUnderVacuum.isEmpty() ? ctidStreams.streamsForCtidSync()
            : ctidStreams.streamsForCtidSync().stream()
                .filter(c -> !streamsUnderVacuum.contains(AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(c)))
                .toList();
    LOGGER.info("Streams to be synced via ctid : {}", finalListOfStreamsToBeSyncedViaCtid.size());
    LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(finalListOfStreamsToBeSyncedViaCtid));
    final FileNodeHandler fileNodeHandler = PostgresQueryUtils.fileNodeForStreams(database,
        finalListOfStreamsToBeSyncedViaCtid,
        quoteString);
    final CdcState defaultCdcState = getDefaultCdcState(postgresDebeziumStateUtil, database);

    final CtidGlobalStateManager ctidStateManager =
        new CtidGlobalStateManager(ctidStreams, fileNodeHandler, stateManager, catalog, savedOffsetAfterReplicationSlotLSN, defaultCdcState);
    return ctidStateManager;

  }

  private static CdcState getDefaultCdcState(final PostgresDebeziumStateUtil postgresDebeziumStateUtil, final JdbcDatabase database) {
    var sourceConfig = database.getSourceConfig();
    final JsonNode initialDebeziumState = postgresDebeziumStateUtil.constructInitialDebeziumState(database,
        sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());
    return new CdcState().withState(initialDebeziumState);
  }

  public static List<AutoCloseableIterator<AirbyteMessage>> cdcCtidIteratorsCombined(final JdbcDatabase database,
                                                                                     final ConfiguredAirbyteCatalog catalog,
                                                                                     final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                                     final StateManager stateManager,
                                                                                     final Instant emittedAt,
                                                                                     final String quoteString,
                                                                                     final CtidGlobalStateManager ctidStateManager,
                                                                                     final boolean savedOffsetAfterReplicationSlotLSN) {
    final JsonNode sourceConfig = database.getSourceConfig();
    final Duration firstRecordWaitTime = PostgresUtils.getFirstRecordWaitTime(sourceConfig);
    final Duration subsequentRecordWaitTime = PostgresUtils.getSubsequentRecordWaitTime(sourceConfig);
    final int queueSize = PostgresUtils.getQueueSize(sourceConfig);
    LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
    LOGGER.info("Queue size: {}", queueSize);

    if (isDebugMode(sourceConfig) && !PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
      throw new ConfigErrorException("WARNING: The config indicates that we are clearing the WAL while reading data. This will mutate the WAL" +
          " associated with the source being debugged and is not advised.");
    }

    final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();

    final JsonNode initialDebeziumState = postgresDebeziumStateUtil.constructInitialDebeziumState(database,
        sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());

    final JsonNode state =
        (stateManager.getCdcStateManager().getCdcState() == null || stateManager.getCdcStateManager().getCdcState().getState() == null)
            ? initialDebeziumState
            : Jsons.clone(stateManager.getCdcStateManager().getCdcState().getState());

    final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(
        Jsons.clone(PostgresCdcProperties.getDebeziumDefaultProperties(database)),
        catalog,
        state,
        sourceConfig);

    // We should always be able to extract offset out of state if it's not null
    if (state != null && savedOffset.isEmpty()) {
      throw new RuntimeException(
          "Unable extract the offset out of state, State mutation might not be working. " + state.asText());
    }

    if (!savedOffsetAfterReplicationSlotLSN) {
      AirbyteTraceMessageUtility.emitAnalyticsTrace(cdcCursorInvalidMessage());
      if (!sourceConfig.get("replication_method").has(INVALID_CDC_CURSOR_POSITION_PROPERTY) || sourceConfig.get("replication_method").get(
          INVALID_CDC_CURSOR_POSITION_PROPERTY).asText().equals(FAIL_SYNC_OPTION)) {
        throw new ConfigErrorException(
            "Saved offset is before replication slot's confirmed lsn. Please reset the connection, and then increase WAL retention and/or increase sync frequency to prevent this from happening in the future. See https://docs.airbyte.com/integrations/sources/postgres/postgres-troubleshooting#under-cdc-incremental-mode-there-are-still-full-refresh-syncs for more details.");
      }
      LOGGER.warn("Saved offset is before Replication slot's confirmed_flush_lsn, Airbyte will trigger sync from scratch");
    } else if (!isDebugMode(sourceConfig) && PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
      // We do not want to acknowledge the WAL logs in debug mode.
      postgresDebeziumStateUtil.commitLSNToPostgresDatabase(database.getDatabaseConfig(),
          savedOffset,
          sourceConfig.get("replication_method").get("replication_slot").asText(),
          sourceConfig.get("replication_method").get("publication").asText(),
          PostgresUtils.getPluginValue(sourceConfig.get("replication_method")));
    }
    final CdcState stateToBeUsed = ctidStateManager.getCdcState();
    final CtidStreams ctidStreams = PostgresCdcCtidUtils.streamsToSyncViaCtid(stateManager.getCdcStateManager(), catalog,
        savedOffsetAfterReplicationSlotLSN);
    final List<AutoCloseableIterator<AirbyteMessage>> initialSyncCtidIterators = new ArrayList<>();
    final List<AirbyteStreamNameNamespacePair> streamsUnderVacuum = new ArrayList<>();
    if (!ctidStreams.streamsForCtidSync().isEmpty()) {
      streamsUnderVacuum.addAll(streamsUnderVacuum(database,
          ctidStreams.streamsForCtidSync(), quoteString).result());

      List<ConfiguredAirbyteStream> finalListOfStreamsToBeSyncedViaCtid =
          streamsUnderVacuum.isEmpty() ? ctidStreams.streamsForCtidSync()
              : ctidStreams.streamsForCtidSync().stream()
                  .filter(c -> !streamsUnderVacuum.contains(AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(c)))
                  .toList();
      final FileNodeHandler fileNodeHandler = PostgresQueryUtils.fileNodeForStreams(database,
          finalListOfStreamsToBeSyncedViaCtid,
          quoteString);
      final PostgresCtidHandler ctidHandler;
      if (!fileNodeHandler.getFailedToQuery().isEmpty()) {
        finalListOfStreamsToBeSyncedViaCtid = finalListOfStreamsToBeSyncedViaCtid.stream()
            .filter(stream -> !fileNodeHandler.getFailedToQuery().contains(
                new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace())))
            .collect(Collectors.toList());
      }
      LOGGER.info("Streams to be synced via ctid : {}", finalListOfStreamsToBeSyncedViaCtid.size());

      try {
        ctidHandler =
            createInitialLoader(database, finalListOfStreamsToBeSyncedViaCtid, fileNodeHandler, quoteString, ctidStateManager,
                Optional.of(
                    new PostgresCdcConnectorMetadataInjector(emittedAt.toString(), io.airbyte.cdk.db.PostgresUtils.getLsn(database).asLong())));
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }

      initialSyncCtidIterators.addAll(ctidHandler.getInitialSyncCtidIterator(
          new ConfiguredAirbyteCatalog().withStreams(finalListOfStreamsToBeSyncedViaCtid), tableNameToTable, emittedAt));
    } else {
      LOGGER.info("No streams will be synced via ctid");
    }

    // Gets the target position.
    final var targetPosition = PostgresCdcTargetPosition.targetPosition(database);
    // Attempt to advance LSN past the target position. For versions of Postgres before PG15, this
    // ensures that there is an event that debezium will
    // receive that is after the target LSN.
    PostgresUtils.advanceLsn(database);
    final AirbyteDebeziumHandler<Long> handler = new AirbyteDebeziumHandler<>(sourceConfig,
        targetPosition, false, firstRecordWaitTime, queueSize, false);
    final PostgresCdcStateHandler postgresCdcStateHandler = new PostgresCdcStateHandler(stateManager);
    final var propertiesManager = new RelationalDbDebeziumPropertiesManager(
        PostgresCdcProperties.getDebeziumDefaultProperties(database), sourceConfig, catalog);
    final var eventConverter = new RelationalDbDebeziumEventConverter(new PostgresCdcConnectorMetadataInjector(), emittedAt);

    final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(
        propertiesManager, eventConverter, new PostgresCdcSavedInfoFetcher(stateToBeUsed), postgresCdcStateHandler);

    if (initialSyncCtidIterators.isEmpty()) {
      return Collections.singletonList(incrementalIteratorSupplier.get());
    }

    if (streamsUnderVacuum.isEmpty()) {
      // This starts processing the WAL as soon as initial sync is complete, this is a bit different from
      // the current cdc syncs.
      // We finish the current CDC once the initial snapshot is complete and the next sync starts
      // processing the WAL
      return Stream
          .of(initialSyncCtidIterators, Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)))
          .flatMap(Collection::stream)
          .collect(Collectors.toList());
    } else {
      LOGGER.warn("Streams are under vacuuming, not going to process WAL");
      return initialSyncCtidIterators;
    }
  }

  public static CdcState getCdcState(final JdbcDatabase database,
                                     final StateManager stateManager) {

    final JsonNode sourceConfig = database.getSourceConfig();
    final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();

    final JsonNode initialDebeziumState = postgresDebeziumStateUtil.constructInitialDebeziumState(database,
        sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());

    return (stateManager.getCdcStateManager().getCdcState() == null
        || stateManager.getCdcStateManager().getCdcState().getState() == null) ? new CdcState().withState(initialDebeziumState)
            : stateManager.getCdcStateManager().getCdcState();
  }

}
