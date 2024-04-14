/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.USE_TEST_CHUNK_SIZE;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.AirbyteMessageHT;
import io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.AirbyteRecordMessageHT;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.TableBlockSize;
import io.airbyte.integrations.source.postgres.PostgresType;
import io.airbyte.integrations.source.postgres.StreamingPostgresDatabase;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations.RowDataWithCtid;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteStream;
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
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCtidHandler {

//  public static class AirbyteMessageHT extends AirbyteMessage {
//    public AirbyteRecordMessageHT recordHT;
//
//    public AirbyteMessageHT(AirbyteRecordMessageHT recordHT) {
//      this.recordHT = recordHT;
//    }
//    @Override
//    public String toString() {
//      return "{\"type\":\"RECORD\",\"record\":" + recordHT + "}";
//    }
//  }

  public static class AirbyteRecordMessageHTSer extends AirbyteRecordMessageHT {
    @Override
    public String toString() {
      StringBuilder sb = new StringBuilder();
//      sb.append(AirbyteRecordMessageHT.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
      sb.append('{');
      sb.append('"');
      sb.append("namespace");
      sb.append('"');
      sb.append(':');
      sb.append('"');
      sb.append(((this.getNamespace() == null)?"<null>":this.getNamespace()));
      sb.append('"');
      sb.append(',');
      sb.append('"');
      sb.append("stream");
      sb.append('"');
      sb.append(':');
      sb.append('"');
      sb.append(((this.getStream() == null)?"<null>":this.getStream()));
      sb.append('"');
      sb.append(',');
      sb.append('"');
      sb.append("data");
      sb.append('"');
      sb.append(':');
      sb.append(((this.getData() == null)?"<null>":this.getData()));
      sb.append(',');
      sb.append('"');
      sb.append("emittedAt");
      sb.append('"');
      sb.append(':');
      sb.append(((this.getEmittedAt() == null)?"<null>":this.getEmittedAt()));
      sb.append(',');
      sb.append('"');
      sb.append("additionalProperties");
      sb.append('"');
      sb.append(':');
      sb.append('"');
      sb.append(((this.getAdditionalProperties() == null)?"<null>":this.getAdditionalProperties()));
      sb.append('"');
      sb.append(',');
      if (sb.charAt((sb.length()- 1)) == ',') {
        sb.setCharAt((sb.length()- 1), '}');
      } else {
        sb.append('}');
      }
      return sb.toString();
    }
  }
  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCtidHandler.class);

  private final JsonNode config;
  private final JdbcDatabase database;
  private final CtidPostgresSourceOperations sourceOperations;
  private final String quoteString;
  private final CtidStateManager ctidStateManager;
  private final FileNodeHandler fileNodeHandler;
  final Map<AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes;
  final Optional<Map<AirbyteStreamNameNamespacePair, Integer>> tablesMaxTuple;
  private final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;
  private final boolean tidRangeScanCapableDBServer;
  private final ExecutorService executor;

  public PostgresCtidHandler(final JsonNode config,
                             final JdbcDatabase database,
                             final CtidPostgresSourceOperations sourceOperations,
                             final String quoteString,
                             final FileNodeHandler fileNodeHandler,
                             final Map<AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes,
                             final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, Integer> tablesMaxTuple,
                             final CtidStateManager ctidStateManager,
                             final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.config = config;
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.fileNodeHandler = fileNodeHandler;
    this.tableBlockSizes = tableBlockSizes;
    this.tablesMaxTuple = Optional.ofNullable(tablesMaxTuple);
    this.ctidStateManager = ctidStateManager;
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
    this.tidRangeScanCapableDBServer = CtidUtils.isTidRangeScanCapableDBServer(database);
    this.executor = Executors.newFixedThreadPool(1);
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getInitialSyncCtidIterator(
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                                final Instant emmitedAt) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = stream.getName();
      final String namespace = stream.getNamespace();
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(namespace, streamName);
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
        LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
        continue;
      }
      if (airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL)) {
        // Grab the selected fields to sync
        final TableInfo<CommonField<PostgresType>> table = tableNameToTable
            .get(fullyQualifiedTableName);
        final List<String> selectedDatabaseFields = table.getFields()
            .stream()
            .map(CommonField::getName)
            .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
            .toList();
        /*final AutoCloseableIterator<RowDataWithCtid> queryStream = queryTableCtid(
            selectedDatabaseFields,
            table.getNameSpace(),
            table.getName(),
            tableBlockSizes.get(pair).tableSize(),
            tableBlockSizes.get(pair).blockSize(),
            tablesMaxTuple.orElseGet(() -> Map.of(pair, -1)).get(pair));
        final AutoCloseableIterator<AirbyteMessageWithCtid> recordIterator =
            getRecordIterator(queryStream, streamName, namespace, emmitedAt.toEpochMilli());*/
//        final AutoCloseableIterator<AirbyteMessage> recordIterator = getFileBasedRecordIterator(
//                selectedDatabaseFields,
//                table.getNameSpace(),
//                table.getName(),
//                tableBlockSizes.get(pair).tableSize(),
//                tableBlockSizes.get(pair).blockSize(),
//                tablesMaxTuple.orElseGet(() -> Map.of(pair, -1)).get(pair), emmitedAt.toEpochMilli());
//        final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, airbyteStream);

        final AutoCloseableIterator<AirbyteRecordMessageHT> recordIteratorHT = getFileBasedRecordIteratorHT(
                selectedDatabaseFields,
                table.getNameSpace(),
                table.getName(),
                tableBlockSizes.get(pair).tableSize(),
                tableBlockSizes.get(pair).blockSize(),
                tablesMaxTuple.orElseGet(() -> Map.of(pair, -1)).get(pair), emmitedAt.toEpochMilli());
        final AutoCloseableIterator<AirbyteMessage> ht = AutoCloseableIterators.transform(recordIteratorHT, r -> new AirbyteMessageHT(r));
//        iteratorList.add(ht);
        final AutoCloseableIterator<AirbyteMessage> logAugmented = augmentWithLogs(ht, pair, streamName);
        iteratorList.add(logAugmented);

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

  private AutoCloseableIterator<AirbyteRecordMessageHT> getFileBasedRecordIteratorHT(
          final List<String> columnNames,
          final String schemaName,
          final String tableName,
          final long tableSize,
          final long blockSize,
          final int maxTuple,
          final long emittedAt) {

    LOGGER.info("Queueing query for table: {}", tableName);
    final var iter = new CopyInitialSyncCtidIterator(ctidStateManager, (StreamingPostgresDatabase) database, sourceOperations, quoteString, columnNames, schemaName, tableName, tableSize,
            blockSize, maxTuple, fileNodeHandler, tidRangeScanCapableDBServer,
            config.has(USE_TEST_CHUNK_SIZE) && config.get(USE_TEST_CHUNK_SIZE).asBoolean(), executor);

    return AutoCloseableIterators.transform(iter, r -> new AirbyteRecordMessageHTSer()
        .withStream(tableName)
        .withNamespace(schemaName)
        .withEmittedAt(emittedAt)
        .withData(r));
  }
  private AutoCloseableIterator<AirbyteMessage> getFileBasedRecordIterator(
          final List<String> columnNames,
          final String schemaName,
          final String tableName,
          final long tableSize,
          final long blockSize,
          final int maxTuple,
          final long emittedAt) {

    LOGGER.info("Queueing query for table: {}", tableName);
    final var iter = new CopyInitialSyncCtidIterator(ctidStateManager, (StreamingPostgresDatabase) database, sourceOperations, quoteString, columnNames, schemaName, tableName, tableSize,
            blockSize, maxTuple, fileNodeHandler, tidRangeScanCapableDBServer,
            config.has(USE_TEST_CHUNK_SIZE) && config.get(USE_TEST_CHUNK_SIZE).asBoolean(), executor);

    return AutoCloseableIterators.transform(iter, r -> new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                    .withStream(tableName)
                    .withNamespace(schemaName)
                    .withEmittedAt(emittedAt)
                    .withData(Jsons.deserialize(r))));
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
            LOGGER.info("Reading stream {}. Records read: {}: {}", streamName, count, r.toString());
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

    ctidStateManager.setStreamStateIteratorFields(streamStateForIncrementalRunSupplier, fileNodeHandler);

    final AirbyteStreamNameNamespacePair pair =
        new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
    return AutoCloseableIterators.transformIterator(
        r -> new SourceStateIterator(r, airbyteStream, ctidStateManager, new StateEmitFrequency(syncCheckpointRecords, syncCheckpointDuration)),
        recordIterator, pair);
  }

}
