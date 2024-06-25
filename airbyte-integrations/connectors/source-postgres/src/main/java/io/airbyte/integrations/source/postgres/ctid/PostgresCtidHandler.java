/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.USE_TEST_CHUNK_SIZE;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.InitialLoadHandler;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.TableBlockSize;
import io.airbyte.integrations.source.postgres.PostgresType;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations.RowDataWithCtid;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCtidHandler implements InitialLoadHandler<PostgresType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCtidHandler.class);

  private final JsonNode config;
  private final JdbcDatabase database;
  private final CtidPostgresSourceOperations sourceOperations;
  private final String quoteString;
  private final CtidStateManager ctidStateManager;
  private final FileNodeHandler fileNodeHandler;
  final Map<AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes;
  final Optional<Map<AirbyteStreamNameNamespacePair, Integer>> tablesMaxTuple;
  private final boolean tidRangeScanCapableDBServer;

  public PostgresCtidHandler(final JsonNode config,
                             final JdbcDatabase database,
                             final CtidPostgresSourceOperations sourceOperations,
                             final String quoteString,
                             final FileNodeHandler fileNodeHandler,
                             final Map<AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes,
                             final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, Integer> tablesMaxTuple,
                             final CtidStateManager ctidStateManager) {
    this.config = config;
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.fileNodeHandler = fileNodeHandler;
    this.tableBlockSizes = tableBlockSizes;
    this.tablesMaxTuple = Optional.ofNullable(tablesMaxTuple);
    this.ctidStateManager = ctidStateManager;
    this.tidRangeScanCapableDBServer = CtidUtils.isTidRangeScanCapableDBServer(database);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> getIteratorForStream(@NotNull ConfiguredAirbyteStream airbyteStream,
                                                                    @NotNull TableInfo<CommonField<PostgresType>> table,
                                                                    @NotNull Instant emittedAt) {
    final AirbyteStream stream = airbyteStream.getStream();
    final String streamName = stream.getName();
    final String namespace = stream.getNamespace();
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);

    final List<String> selectedDatabaseFields = table.getFields()
        .stream()
        .map(CommonField::getName)
        .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
        .toList();
    final AutoCloseableIterator<RowDataWithCtid> queryStream = queryTableCtid(
        selectedDatabaseFields,
        table.getNameSpace(),
        table.getName(),
        tableBlockSizes.get(pair).tableSize(),
        tableBlockSizes.get(pair).blockSize(),
        tablesMaxTuple.orElseGet(() -> Map.of(pair, -1)).get(pair));
    final AutoCloseableIterator<AirbyteMessageWithCtid> recordIterator =
        getRecordIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
    final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, airbyteStream);
    return augmentWithLogs(recordAndMessageIterator, pair, streamName);
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getInitialSyncCtidIterator(
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                                final Instant emmitedAt,
                                                                                final boolean decorateWithStartedStatus,
                                                                                final boolean decorateWithCompletedStatus) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = stream.getName();
      final String namespace = stream.getNamespace();
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(namespace, streamName);
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
        LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
        continue;
      }
      if (airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL)) {

        final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
        if (decorateWithStartedStatus) {
          iteratorList.add(
              new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(pair, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED)));
        }

        // Grab the selected fields to sync
        final TableInfo<CommonField<PostgresType>> table = tableNameToTable
            .get(fullyQualifiedTableName);
        final var iterator = getIteratorForStream(airbyteStream, table, emmitedAt);
        iteratorList.add(iterator);

        if (decorateWithCompletedStatus) {
          iteratorList.add(new StreamStatusTraceEmitterIterator(
              new AirbyteStreamStatusHolder(pair, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)));
        }
      }
    }
    return iteratorList;
  }

  private AutoCloseableIterator<RowDataWithCtid> queryTableCtid(
                                                                final List<String> columnNames,
                                                                final String schemaName,
                                                                final String tableName,
                                                                final long tableSize,
                                                                final long blockSize,
                                                                final int maxTuple) {

    LOGGER.info("Queueing query for table: {}", tableName);
    return new InitialSyncCtidIterator(ctidStateManager, database, sourceOperations, quoteString, columnNames, schemaName, tableName, tableSize,
        blockSize, maxTuple, fileNodeHandler, tidRangeScanCapableDBServer,
        config.has(USE_TEST_CHUNK_SIZE) && config.get(USE_TEST_CHUNK_SIZE).asBoolean());
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private AutoCloseableIterator<AirbyteMessageWithCtid> getRecordIterator(
                                                                          final AutoCloseableIterator<RowDataWithCtid> recordIterator,
                                                                          final String streamName,
                                                                          final String namespace,
                                                                          final long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessageWithCtid(new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withEmittedAt(emittedAt)
            .withData(r.recordData().rawRowData())
            .withMeta(isMetaChangesEmptyOrNull(r.recordData().meta()) ? null : r.recordData().meta())),
        r.ctid()));
  }

  private boolean isMetaChangesEmptyOrNull(AirbyteRecordMessageMeta meta) {
    return meta == null || meta.getChanges() == null || meta.getChanges().isEmpty();
  }

  // Augments the given iterator with record count logs.
  private AutoCloseableIterator<AirbyteMessage> augmentWithLogs(final AutoCloseableIterator<AirbyteMessage> iterator,
                                                                final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair,
                                                                final String streamName) {
    final AtomicLong recordCount = new AtomicLong();
    return AutoCloseableIterators.transform(iterator,
        AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()),
        r -> {
          final long count = recordCount.incrementAndGet();
          if (count % 1_000_000 == 0) {
            LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
          }
          return r;
        });
  }

  private AutoCloseableIterator<AirbyteMessage> augmentWithState(final AutoCloseableIterator<AirbyteMessageWithCtid> recordIterator,
                                                                 final ConfiguredAirbyteStream airbyteStream) {

    final Duration syncCheckpointDuration =
        config.get(SYNC_CHECKPOINT_DURATION_PROPERTY) != null ? Duration.ofSeconds(config.get(SYNC_CHECKPOINT_DURATION_PROPERTY).asLong())
            : DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY) != null ? config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY).asLong()
        : DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS;

    final AirbyteStreamNameNamespacePair pair =
        new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
    return AutoCloseableIterators.transformIterator(
        r -> new SourceStateIterator(r, airbyteStream, ctidStateManager, new StateEmitFrequency(syncCheckpointRecords, syncCheckpointDuration)),
        recordIterator, pair);
  }

}
