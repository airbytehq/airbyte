package io.airbyte.integrations.source.postgres.cdc;

import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.streamsUnderVacuum;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.internals.postgres.PostgresCdcTargetPosition;
import io.airbyte.integrations.debezium.internals.postgres.PostgresDebeziumStateUtil;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.TableBlockSize;
import io.airbyte.integrations.source.postgres.PostgresType;
import io.airbyte.integrations.source.postgres.PostgresUtils;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcCtidUtils.CtidStreams;
import io.airbyte.integrations.source.postgres.ctid.CtidGlobalStateManager;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations.CdcMetadataInjector;
import io.airbyte.integrations.source.postgres.ctid.CtidStateManager;
import io.airbyte.integrations.source.postgres.ctid.PostgresCtidHandler;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
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
import java.util.OptionalInt;
import java.util.OptionalLong;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCdcCtidInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcCtidInitializer.class);

  public static List<AutoCloseableIterator<AirbyteMessage>> cdcCtidIteratorsCombined(final JdbcDatabase database,
      final ConfiguredAirbyteCatalog catalog,
      final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
      final StateManager stateManager,
      final Instant emittedAt,
      final String quoteString,
      final JsonNode replicationSlot) {
    try {
      final JsonNode sourceConfig = database.getSourceConfig();
      final Duration firstRecordWaitTime = PostgresUtils.getFirstRecordWaitTime(sourceConfig);
      final OptionalInt queueSize = OptionalInt.of(PostgresUtils.getQueueSize(sourceConfig));
      LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
      LOGGER.info("Queue size: {}", queueSize.getAsInt());

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

      final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(
          // We can assume that there will be only 1 replication slot cause before the sync starts for
          // Postgres CDC,
          // we run all the check operations and one of the check validates that the replication slot exists
          // and has only 1 entry
          replicationSlot,
          savedOffset);

      if (!savedOffsetAfterReplicationSlotLSN) {
        LOGGER.warn("Saved offset is before Replication slot's confirmed_flush_lsn, Airbyte will trigger sync from scratch");
      } else if (PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
        postgresDebeziumStateUtil.commitLSNToPostgresDatabase(database.getDatabaseConfig(),
            savedOffset,
            sourceConfig.get("replication_method").get("replication_slot").asText(),
            sourceConfig.get("replication_method").get("publication").asText(),
            PostgresUtils.getPluginValue(sourceConfig.get("replication_method")));
      }
      final CdcState stateToBeUsed = (!savedOffsetAfterReplicationSlotLSN || stateManager.getCdcStateManager().getCdcState() == null
          || stateManager.getCdcStateManager().getCdcState().getState() == null) ? new CdcState().withState(initialDebeziumState)
          : stateManager.getCdcStateManager().getCdcState();
      final CtidStreams ctidStreams = PostgresCdcCtidUtils.streamsToSyncViaCtid(stateManager.getCdcStateManager(), catalog,
          savedOffsetAfterReplicationSlotLSN);
      final List<AutoCloseableIterator<AirbyteMessage>> ctidIterator = new ArrayList<>();
      final List<AirbyteStreamNameNamespacePair> streamsUnderVacuum = new ArrayList<>();
      if (!ctidStreams.streamsForCtidSync().isEmpty()) {
        streamsUnderVacuum.addAll(streamsUnderVacuum(database,
            ctidStreams.streamsForCtidSync(), quoteString));

        final List<ConfiguredAirbyteStream> finalListOfStreamsToBeSyncedViaCtid =
            streamsUnderVacuum.isEmpty() ? ctidStreams.streamsForCtidSync()
                : ctidStreams.streamsForCtidSync().stream()
                    .filter(c -> !streamsUnderVacuum.contains(AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(c)))
                    .toList();
        LOGGER.info("Streams to be synced via ctid : {}", finalListOfStreamsToBeSyncedViaCtid.size());
        final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, Long> fileNodes = PostgresQueryUtils.fileNodeForStreams(database,
            finalListOfStreamsToBeSyncedViaCtid,
            quoteString);
        final CtidStateManager ctidStateManager = new CtidGlobalStateManager(ctidStreams, fileNodes, stateToBeUsed, catalog);
        final CtidPostgresSourceOperations ctidPostgresSourceOperations = new CtidPostgresSourceOperations(
            Optional.of(new CdcMetadataInjector(
                emittedAt.toString(), io.airbyte.db.PostgresUtils.getLsn(database).asLong(), new PostgresCdcConnectorMetadataInjector())));
        final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes =
            PostgresQueryUtils.getTableBlockSizeForStream(
                database,
                finalListOfStreamsToBeSyncedViaCtid,
                quoteString);
        final PostgresCtidHandler ctidHandler = new PostgresCtidHandler(sourceConfig, database,
            ctidPostgresSourceOperations,
            quoteString,
            fileNodes,
            tableBlockSizes,
            ctidStateManager,
            namespacePair -> Jsons.emptyObject());

        ctidIterator.addAll(ctidHandler.getIncrementalIterators(
            new ConfiguredAirbyteCatalog().withStreams(finalListOfStreamsToBeSyncedViaCtid), tableNameToTable, emittedAt));
      } else {
        LOGGER.info("No streams will be synced via ctid");
      }

      final AirbyteDebeziumHandler<Long> handler = new AirbyteDebeziumHandler<>(sourceConfig,
          PostgresCdcTargetPosition.targetPosition(database), false, firstRecordWaitTime, queueSize);
      final PostgresCdcStateHandler postgresCdcStateHandler = new PostgresCdcStateHandler(stateManager);

      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
          new PostgresCdcSavedInfoFetcher(stateToBeUsed),
          postgresCdcStateHandler,
          new PostgresCdcConnectorMetadataInjector(),
          PostgresCdcProperties.getDebeziumDefaultProperties(database),
          emittedAt,
          false);

      if (ctidIterator.isEmpty()) {
        return Collections.singletonList(incrementalIteratorSupplier.get());
      }

      if (streamsUnderVacuum.isEmpty()) {
        // This starts processing the WAL as soon as initial sync is complete, this is a bit different from the current cdc syncs.
        // We finish the current CDC once the initial snapshot is complete and the next sync starts processing the WAL
        return Stream
            .of(ctidIterator, Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)))
            .flatMap(Collection::stream)
            .collect(Collectors.toList());
      } else {
        LOGGER.warn("Streams are under vacuuming, not going to process WAL");
        return ctidIterator;
      }

    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }
}
