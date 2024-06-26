/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_COLUMN_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_DATABASE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_SCHEMA_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_TABLE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_TYPE;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.SqlDatabase;
import io.airbyte.cdk.db.jdbc.AirbyteRecordData;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
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
import io.airbyte.integrations.source.mssql.MssqlQueryUtils.TableSizeInfo;
import io.airbyte.integrations.source.mssql.MssqlSourceOperations;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import java.sql.DatabaseMetaData;
import java.sql.JDBCType;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlInitialLoadHandler implements InitialLoadHandler<JDBCType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlInitialLoadHandler.class);
  private static final long RECORD_LOGGING_SAMPLE_RATE = 1_000_000;
  private final JsonNode config;
  private final JdbcDatabase database;
  private final MssqlSourceOperations sourceOperations;
  private final String quoteString;
  private final MssqlInitialLoadStateManager initialLoadStateManager;
  private final Optional<Function<AirbyteStreamNameNamespacePair, JsonNode>> streamStateForIncrementalRunSupplier;
  private static final long QUERY_TARGET_SIZE_GB = 1_073_741_824;
  private static final long DEFAULT_CHUNK_SIZE = 1_000_000;
  final Map<AirbyteStreamNameNamespacePair, TableSizeInfo> tableSizeInfoMap;

  public MssqlInitialLoadHandler(
                                 final JsonNode config,
                                 final JdbcDatabase database,
                                 final MssqlSourceOperations sourceOperations,
                                 final String quoteString,
                                 final MssqlInitialLoadStateManager initialLoadStateManager,
                                 final Optional<Function<AirbyteStreamNameNamespacePair, JsonNode>> streamStateForIncrementalRunSupplier,
                                 final Map<AirbyteStreamNameNamespacePair, TableSizeInfo> tableSizeInfoMap) {
    this.config = config;
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.initialLoadStateManager = initialLoadStateManager;
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
    this.tableSizeInfoMap = tableSizeInfoMap;
  }

  private static String getCatalog(final SqlDatabase database) {
    return (database.getSourceConfig().has(JdbcUtils.DATABASE_KEY) ? database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText() : null);
  }

  public static String discoverClusteredIndexForStream(final JdbcDatabase database,
                                                       final AirbyteStream stream) {
    Map<String, String> clusteredIndexes = new HashMap<>();
    try {
      // Get all clustered index names without specifying a table name
      clusteredIndexes = aggregateClusteredIndexes(database.bufferedResultSetQuery(
          connection -> connection.getMetaData().getIndexInfo(getCatalog(database), stream.getNamespace(), stream.getName(), false, false),
          r -> {
            if (r.getShort(JDBC_COLUMN_TYPE) == DatabaseMetaData.tableIndexClustered) {
              final String schemaName =
                  r.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? r.getString(JDBC_COLUMN_SCHEMA_NAME) : r.getString(JDBC_COLUMN_DATABASE_NAME);
              final String streamName = JdbcUtils.getFullyQualifiedTableName(schemaName, r.getString(JDBC_COLUMN_TABLE_NAME));
              final String columnName = r.getString(JDBC_COLUMN_COLUMN_NAME);
              return new ClusteredIndexAttributesFromDb(streamName, columnName);
            } else {
              return null;
            }
          }));
    } catch (final SQLException e) {
      LOGGER.debug(String.format("Could not retrieve clustered indexes without a table name (%s), not blocking, fall back to use pk.", e));
    }
    return clusteredIndexes.getOrDefault(stream.getName(), null);
  }

  @VisibleForTesting
  public record ClusteredIndexAttributesFromDb(String streamName,
                                               String columnName) {}

  /**
   * Aggregate list of @param entries of StreamName and clustered index column name
   *
   * @return a map by StreamName to associated columns in clustered index. If clustered index has
   *         multiple columns, we always use the first column.
   */
  @VisibleForTesting
  static Map<String, String> aggregateClusteredIndexes(final List<ClusteredIndexAttributesFromDb> entries) {
    final Map<String, String> result = new HashMap<>();
    entries.forEach(entry -> {
      if (entry == null) {
        return;
      }
      if (result.containsKey(entry.streamName())) {
        return;
      }
      result.put(entry.streamName, entry.columnName());
    });
    return result;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                             final Instant emittedAt,
                                                                             final boolean decorateWithStartedStatus,
                                                                             final boolean decorateWithCompletedStatus) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = stream.getName();
      final String namespace = stream.getNamespace();
      // TODO: need to select column according to indexing status of table. may not be primary key
      final var pair = new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(streamName, namespace);
      if (airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL)) {
        final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(namespace, streamName);

        // Grab the selected fields to sync
        final TableInfo<CommonField<JDBCType>> table = tableNameToTable.get(fullyQualifiedTableName);
        if (decorateWithStartedStatus) {
          iteratorList.add(
              new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(pair, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED)));
        }
        iteratorList.add(getIteratorForStream(airbyteStream, table, emittedAt));
        if (decorateWithCompletedStatus) {
          iteratorList.add(new StreamStatusTraceEmitterIterator(
              new AirbyteStreamStatusHolder(pair, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)));
        }
      }
    }
    return iteratorList;
  }

  @NotNull
  @Override
  public AutoCloseableIterator<AirbyteMessage> getIteratorForStream(@NotNull final ConfiguredAirbyteStream airbyteStream,
                                                                    @NotNull final TableInfo<CommonField<JDBCType>> table,
                                                                    @NotNull final Instant emittedAt) {
    final AirbyteStream stream = airbyteStream.getStream();
    final String streamName = stream.getName();
    final String namespace = stream.getNamespace();
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
    final List<String> selectedDatabaseFields = table.getFields()
        .stream()
        .map(CommonField::getName)
        .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
        .toList();
    final AutoCloseableIterator<AirbyteRecordData> queryStream =
        new MssqlInitialLoadRecordIterator(database, sourceOperations, quoteString, initialLoadStateManager, selectedDatabaseFields, pair,
            calculateChunkSize(tableSizeInfoMap.get(pair), pair), isCompositePrimaryKey(airbyteStream));
    final AutoCloseableIterator<AirbyteMessage> recordIterator =
        getRecordIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
    final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, airbyteStream);
    return augmentWithLogs(recordAndMessageIterator, pair, streamName);
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private AutoCloseableIterator<AirbyteMessage> getRecordIterator(
                                                                  final AutoCloseableIterator<AirbyteRecordData> recordIterator,
                                                                  final String streamName,
                                                                  final String namespace,
                                                                  final long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withEmittedAt(emittedAt)
            .withData(r.rawRowData())
            .withMeta(isMetaChangesEmptyOrNull(r.meta()) ? null : r.meta())));
  }

  private boolean isMetaChangesEmptyOrNull(AirbyteRecordMessageMeta meta) {
    return meta == null || meta.getChanges() == null || meta.getChanges().isEmpty();
  }

  // Augments the given iterator with record count logs.
  private AutoCloseableIterator<AirbyteMessage> augmentWithLogs(final AutoCloseableIterator<AirbyteMessage> iterator,
                                                                final AirbyteStreamNameNamespacePair pair,
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
                                                                 final ConfiguredAirbyteStream airbyteStream) {
    final AirbyteStreamNameNamespacePair pair =
        new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());

    final Duration syncCheckpointDuration =
        config.get(SYNC_CHECKPOINT_DURATION_PROPERTY) != null
            ? Duration.ofSeconds(config.get(SYNC_CHECKPOINT_DURATION_PROPERTY).asLong())
            : DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY) != null ? config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY).asLong()
        : DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS;

    streamStateForIncrementalRunSupplier.ifPresent(initialLoadStateManager::setStreamStateForIncrementalRunSupplier);
    return AutoCloseableIterators.transformIterator(
        r -> new SourceStateIterator<>(r, airbyteStream, initialLoadStateManager,
            new StateEmitFrequency(syncCheckpointRecords, syncCheckpointDuration)),
        recordIterator, new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(pair.getName(), pair.getNamespace()));
  }

  private static boolean isCompositePrimaryKey(final ConfiguredAirbyteStream stream) {
    return stream.getStream().getSourceDefinedPrimaryKey().size() > 1;
  }

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

}
