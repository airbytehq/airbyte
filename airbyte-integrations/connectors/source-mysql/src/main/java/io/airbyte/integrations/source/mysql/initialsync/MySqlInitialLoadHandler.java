/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mysql.cj.MysqlType;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mysql.MySqlQueryUtils.TableSizeInfo;
import io.airbyte.integrations.source.mysql.MySqlSourceOperations;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
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
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlInitialLoadHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialLoadHandler.class);

  private static final long RECORD_LOGGING_SAMPLE_RATE = 1_000_000;
  private final JsonNode config;
  private final JdbcDatabase database;
  private final MySqlSourceOperations sourceOperations;
  private final String quoteString;
  private final MySqlInitialLoadStateManager initialLoadStateManager;
  private final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  private static final long QUERY_TARGET_SIZE_GB = 1_073_741_824;
  private static final long DEFAULT_CHUNK_SIZE = 1_000_000;
  final Map<AirbyteStreamNameNamespacePair, TableSizeInfo> tableSizeInfoMap;

  public MySqlInitialLoadHandler(final JsonNode config,
                                 final JdbcDatabase database,
                                 final MySqlSourceOperations sourceOperations,
                                 final String quoteString,
                                 final MySqlInitialLoadStateManager initialLoadStateManager,
                                 final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier,
                                 final Map<AirbyteStreamNameNamespacePair, TableSizeInfo> tableSizeInfoMap) {
    this.config = config;
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.initialLoadStateManager = initialLoadStateManager;
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
    this.tableSizeInfoMap = tableSizeInfoMap;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                                                             final Instant emittedAt) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = stream.getName();
      final String namespace = stream.getNamespace();
      final List<String> primaryKeys = stream.getSourceDefinedPrimaryKey().stream().flatMap(pk -> Stream.of(pk.get(0))).toList();
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(namespace, streamName);
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
        LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
        continue;
      }
      if (airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL)) {
        // Grab the selected fields to sync
        final TableInfo<CommonField<MysqlType>> table = tableNameToTable
            .get(fullyQualifiedTableName);
        final List<String> selectedDatabaseFields = table.getFields()
            .stream()
            .map(CommonField::getName)
            .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
            .collect(Collectors.toList());

        // This is to handle the case if the user de-selects the PK column
        // Necessary to query the data via pk but won't be added to the final record
        primaryKeys.forEach(pk -> {
          if (!selectedDatabaseFields.contains(pk)) {
            selectedDatabaseFields.add(0, pk);
          }
        });

        final AutoCloseableIterator<JsonNode> queryStream =
            new MySqlInitialLoadRecordIterator(database, sourceOperations, quoteString, initialLoadStateManager, selectedDatabaseFields, pair,
                calculateChunkSize(tableSizeInfoMap.get(pair), pair), isCompositePrimaryKey(airbyteStream));
        final AutoCloseableIterator<AirbyteMessage> recordIterator =
            getRecordIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
        final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, pair);

        iteratorList.add(augmentWithLogs(recordAndMessageIterator, pair, streamName));

      }
    }
    return iteratorList;
  }

  private static boolean isCompositePrimaryKey(final ConfiguredAirbyteStream stream) {
    return stream.getStream().getSourceDefinedPrimaryKey().size() > 1;
  }

  // Calculates the number of rows to fetch per query.
  @VisibleForTesting
  public static long calculateChunkSize(final TableSizeInfo tableSizeInfo, final AirbyteStreamNameNamespacePair pair) {
    // If table size info could not be calculated, a default chunk size will be provided.
    if (tableSizeInfo == null || tableSizeInfo.tableSize() == 0 || tableSizeInfo.avgRowLength() == 0) {
      LOGGER.info("Chunk size could not be determined for pair: {}, defaulting to {} rows", pair, DEFAULT_CHUNK_SIZE);
      return DEFAULT_CHUNK_SIZE;
    }
    final long avgRowLength = tableSizeInfo.avgRowLength();
    final long chunkSize = QUERY_TARGET_SIZE_GB / avgRowLength;
    LOGGER.info("Chunk size determined for pair: {}, is {}", pair, chunkSize);
    return chunkSize;
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private AutoCloseableIterator<AirbyteMessage> getRecordIterator(
                                                                  final AutoCloseableIterator<JsonNode> recordIterator,
                                                                  final String streamName,
                                                                  final String namespace,
                                                                  final long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withEmittedAt(emittedAt)
            .withData(r)));
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
          if (count % RECORD_LOGGING_SAMPLE_RATE == 0) {
            LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
          }
          return r;
        });
  }

  private AutoCloseableIterator<AirbyteMessage> augmentWithState(final AutoCloseableIterator<AirbyteMessage> recordIterator,
                                                                 final AirbyteStreamNameNamespacePair pair) {

    final PrimaryKeyLoadStatus currentPkLoadStatus = initialLoadStateManager.getPrimaryKeyLoadStatus(pair);
    final JsonNode incrementalState =
        (currentPkLoadStatus == null || currentPkLoadStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
            : currentPkLoadStatus.getIncrementalState();

    final Duration syncCheckpointDuration =
        config.get(SYNC_CHECKPOINT_DURATION_PROPERTY) != null ? Duration.ofSeconds(config.get(SYNC_CHECKPOINT_DURATION_PROPERTY).asLong())
            : MySqlInitialSyncStateIterator.SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY) != null ? config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY).asLong()
        : MySqlInitialSyncStateIterator.SYNC_CHECKPOINT_RECORDS;

    return AutoCloseableIterators.transformIterator(
        r -> new MySqlInitialSyncStateIterator(r, pair, initialLoadStateManager, incrementalState,
            syncCheckpointDuration, syncCheckpointRecords),
        recordIterator, pair);
  }

}
