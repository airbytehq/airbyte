/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.cdk.components.debezium.DebeziumComponent;
import io.airbyte.cdk.components.debezium.DebeziumEngineManager;
import io.airbyte.cdk.db.PgLsn;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.TableBlockSize;
import io.airbyte.integrations.source.postgres.PostgresType;
import io.airbyte.integrations.source.postgres.PostgresUtils;
import io.airbyte.integrations.source.postgres.ctid.CtidGlobalStateManager;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations.CdcMetadataInjector;
import io.airbyte.integrations.source.postgres.ctid.CtidStateManager;
import io.airbyte.integrations.source.postgres.ctid.CtidUtils;
import io.airbyte.integrations.source.postgres.ctid.FileNodeHandler;
import io.airbyte.integrations.source.postgres.ctid.PostgresCtidHandler;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static io.airbyte.cdk.db.DbAnalyticsUtils.cdcCursorInvalidMessage;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.streamsUnderVacuum;
import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.FAIL_SYNC_OPTION;
import static io.airbyte.integrations.source.postgres.PostgresSpecConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.postgres.PostgresUtils.isDebugMode;
import static io.airbyte.integrations.source.postgres.PostgresUtils.prettyPrintConfiguredAirbyteStreamList;

public class PostgresCdcCtidInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcCtidInitializer.class);

  public static List<AutoCloseableIterator<AirbyteMessage>> cdcCtidIteratorsCombined(
      final JdbcDatabase database,
      final ConfiguredAirbyteCatalog catalog,
      final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
      final StateManager stateManager,
      final Instant emittedAt,
      final String quoteString,
      final JsonNode replicationSlot) {
    try {
      final JsonNode sourceConfig = database.getSourceConfig();

      if (isDebugMode(sourceConfig) && !PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
        throw new ConfigErrorException("WARNING: The config indicates that we are clearing the WAL while reading data. This will mutate the WAL" +
            " associated with the source being debugged and is not advised.");
      }

      var initialDebeziumState = PostgresLsnMapper.makeSyntheticDebeziumState(database, sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());

      var currentState =
          (stateManager.getCdcStateManager().getCdcState() == null || stateManager.getCdcStateManager().getCdcState().getState() == null)
              ? initialDebeziumState
              : toComponentState(stateManager);

      final var currentLsn = new PostgresLsnMapper().get(currentState.offset());

      final boolean savedOffsetAfterReplicationSlotLSN = PostgresLsnMapper.isSavedOffsetAfterReplicationSlotLSN(
          // We can assume that there will be only 1 replication slot cause before the sync starts for
          // Postgres CDC,
          // we run all the check operations and one of the check validates that the replication slot exists
          // and has only 1 entry
          replicationSlot,
          currentLsn);

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
        PostgresLsnMapper.commitLSNToPostgresDatabase(
            database,
            currentLsn,
            sourceConfig.get("replication_method").get("replication_slot").asText(),
            sourceConfig.get("replication_method").get("publication").asText(),
            PostgresUtils.getPluginValue(sourceConfig.get("replication_method")));
      }
      final CdcState stateToBeUsed = (!savedOffsetAfterReplicationSlotLSN
          || stateManager.getCdcStateManager().getCdcState() == null
          || stateManager.getCdcStateManager().getCdcState().getState() == null)
          ? new CdcState().withState(fromComponentState(initialDebeziumState))
          : stateManager.getCdcStateManager().getCdcState();
      final PostgresCdcCtidUtils.CtidStreams ctidStreams = PostgresCdcCtidUtils.streamsToSyncViaCtid(stateManager.getCdcStateManager(), catalog,
          savedOffsetAfterReplicationSlotLSN);
      final List<AutoCloseableIterator<AirbyteMessage>> initialSyncCtidIterators = new ArrayList<>();
      final List<AirbyteStreamNameNamespacePair> streamsUnderVacuum = new ArrayList<>();
      if (!ctidStreams.streamsForCtidSync().isEmpty()) {
        streamsUnderVacuum.addAll(streamsUnderVacuum(database,
            ctidStreams.streamsForCtidSync(), quoteString).result());

        final List<ConfiguredAirbyteStream> finalListOfStreamsToBeSyncedViaCtid =
            streamsUnderVacuum.isEmpty() ? ctidStreams.streamsForCtidSync()
                : ctidStreams.streamsForCtidSync().stream()
                .filter(c -> !streamsUnderVacuum.contains(AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(c)))
                .toList();
        LOGGER.info("Streams to be synced via ctid : {}", finalListOfStreamsToBeSyncedViaCtid.size());
        LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(finalListOfStreamsToBeSyncedViaCtid));
        final FileNodeHandler fileNodeHandler = PostgresQueryUtils.fileNodeForStreams(
            database,
            finalListOfStreamsToBeSyncedViaCtid,
            quoteString);
        final CtidStateManager ctidStateManager = new CtidGlobalStateManager(ctidStreams, fileNodeHandler, stateToBeUsed, catalog);
        final CtidPostgresSourceOperations ctidPostgresSourceOperations = new CtidPostgresSourceOperations(
            Optional.of(new CdcMetadataInjector(
                emittedAt.toString(), io.airbyte.cdk.db.PostgresUtils.getLsn(database).asLong())));
        final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes =
            PostgresQueryUtils.getTableBlockSizeForStreams(
                database,
                finalListOfStreamsToBeSyncedViaCtid,
                quoteString);

        final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, Integer> tablesMaxTuple =
            CtidUtils.isTidRangeScanCapableDBServer(database) ? null
                : PostgresQueryUtils.getTableMaxTupleForStreams(database, finalListOfStreamsToBeSyncedViaCtid, quoteString);

        final PostgresCtidHandler ctidHandler = new PostgresCtidHandler(sourceConfig, database,
            ctidPostgresSourceOperations,
            quoteString,
            fileNodeHandler,
            tableBlockSizes,
            tablesMaxTuple,
            ctidStateManager,
            namespacePair -> Jsons.emptyObject());

        initialSyncCtidIterators.addAll(ctidHandler.getInitialSyncCtidIterator(
            new ConfiguredAirbyteCatalog().withStreams(finalListOfStreamsToBeSyncedViaCtid), tableNameToTable, emittedAt));
      } else {
        LOGGER.info("No streams will be synced via ctid");
      }

      final var config = PostgresDebeziumComponentConfigBuilder.builder()
          .withUpperBound(initialDebeziumState.offset())
          .withConfig(database)
          .withCatalog(catalog)
          .build();
      // Attempt to advance LSN past the target position. For versions of Postgres before PG15, this
      // ensures that there is an event that debezium will
      // receive that is after the target LSN.
      PostgresUtils.advanceLsn(database);
      final var input = new DebeziumComponent.Input(config, currentState);
      final var lazyDebeziumIterable = DebeziumEngineManager.debeziumComponent().collectRepeatedly(input);
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () ->
        new CdcIterator(lazyDebeziumIterable.iterator(), stateManager, emittedAt);

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
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  static class CdcIterator extends AbstractIterator<AirbyteMessage> implements AutoCloseableIterator<AirbyteMessage> {

    private final Iterator<DebeziumComponent.Output> outputIterator;
    private final StateManager stateManager;
    private final Instant emittedAt;

    private Iterator<AirbyteMessage> messageIterator;

    public CdcIterator(Iterator<DebeziumComponent.Output> outputIterator, StateManager stateManager, Instant emittedAt) {
      this.outputIterator = outputIterator;
      this.stateManager = stateManager;
      this.emittedAt = emittedAt;
      this.messageIterator = nextIterator(outputIterator.next());
    }

    @Override
    public void close() {
      endOfData();
    }

    @Nullable
    @Override
    protected AirbyteMessage computeNext() {
      if (!messageIterator.hasNext()) {
        if (!outputIterator.hasNext()) {
          return endOfData();
        }
        messageIterator = nextIterator(outputIterator.next());
      }
      return messageIterator.next();
    }

    private Iterator<AirbyteMessage> nextIterator(final DebeziumComponent.Output output) {
      return new Iterator<>() {
        private Iterator<DebeziumComponent.Record> recordIterator = output.data().iterator();

        @Override
        public boolean hasNext() {
          return recordIterator != null;
        }

        @Override
        public AirbyteMessage next() {
          if (recordIterator == null) {
            throw new NoSuchElementException();
          }
          if (recordIterator.hasNext()) {
            return toAirbyteRecordMessage(recordIterator.next(), emittedAt);
          } else {
            recordIterator = null;
            return toAirbyteStateMessage(stateManager, output);
          }
        }
      };
    }
  }


  static public DebeziumComponent.State toComponentState(StateManager stateManager) {
    var state = (ObjectNode) stateManager.getCdcStateManager().getCdcState().getState();
    Map<JsonNode, JsonNode> debeziumValues = new HashMap<>();
    var iterator = state.fields();
    while (iterator.hasNext()) {
      var e = iterator.next();
      debeziumValues.put(Jsons.deserialize(e.getKey()), Jsons.deserialize(e.getValue().asText()));
    }
    return new DebeziumComponent.State(new DebeziumComponent.State.Offset(debeziumValues), Optional.empty());
  }

  static public AirbyteMessage toAirbyteRecordMessage(DebeziumComponent.Record record, Instant emittedAt) {
    final ObjectNode data;
    final Instant transactionTimestamp = Instant.ofEpochMilli(record.source().get("ts_ms").asLong());
    if (record.after().isNull()) {
      data = (ObjectNode) Jsons.clone(record.before());
      data.put(CDC_DELETED_AT, transactionTimestamp.toString());
    } else {
      data = (ObjectNode) Jsons.clone(record.after());
      data.put(CDC_DELETED_AT, (String) null);
    }
    data.put(CDC_UPDATED_AT, transactionTimestamp.toString());
    data.put(CDC_LSN, record.source().get("lsn").asLong());

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(record.source().get("table").asText())
            .withNamespace(record.source().get("schema").asText())
            .withEmittedAt(emittedAt.toEpochMilli())
            .withData(data));
  }

  static public String CDC_LSN = "_ab_cdc_lsn";
  static public String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  static public String CDC_DELETED_AT = "_ab_cdc_deleted_at";

  static public JsonNode fromComponentState(DebeziumComponent.State state) {
    final var json = (ObjectNode) Jsons.emptyObject();
    state.offset().debeziumOffset().forEach((k, v) -> json.put(Jsons.serialize(k), Jsons.serialize(v)));
    return json;
  }

  static public AirbyteMessage toAirbyteStateMessage(StateManager stateManager, DebeziumComponent.Output output) {
    final JsonNode asJson = fromComponentState(output.state());
    LOGGER.info("debezium state: {}", asJson);
    stateManager.getCdcStateManager().setCdcState(new CdcState().withState(asJson));
    /*
     * Namespace pair is ignored by global state manager, but is needed for satisfy the API contract.
     * Therefore, provide an empty optional.
     */
    final AirbyteStateMessage stateMessage = stateManager.emit(Optional.empty())
        .withSourceStats(new AirbyteStateStats().withRecordCount((double) output.executionSummary().records().count()));
    return new AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage);
  }
}