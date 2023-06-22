/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.postgres.PostgresType;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.integrations.source.relationaldb.TableInfo;
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
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresXminHandler {

  private final JdbcCompatibleSourceOperations sourceOperations;
  private final JdbcDatabase database;
  private final String quoteString;
  private final XminStatus currentXminStatus;
  private final XminStateManager xminStateManager;

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresXminHandler.class);

  public PostgresXminHandler(final JdbcDatabase database,
                             final JdbcCompatibleSourceOperations sourceOperations,
                             final String quoteString,
                             final XminStatus xminStatus,
                             final XminStateManager xminStateManager) {
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.currentXminStatus = xminStatus;
    this.xminStateManager = xminStateManager;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                             final Instant emittedAt) {

    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    /*
     */
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = airbyteStream.getStream().getName();
      final String namespace = airbyteStream.getStream().getNamespace();
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName,
          namespace);

      // Skip syncing the stream if it doesn't exist in the source.
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getNamespace(),
          stream.getName());
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
            .collect(Collectors.toList());

        final AutoCloseableIterator<JsonNode> queryStream = queryTableXmin(selectedDatabaseFields, table.getNameSpace(), table.getName());
        final AutoCloseableIterator<AirbyteMessage> recordIterator =
            getRecordIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
        final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, pair);

        iteratorList.add(augmentWithLogs(recordAndMessageIterator, pair, streamName));
      }
    }

    return iteratorList;
  }

  private AutoCloseableIterator<JsonNode> queryTableXmin(
                                                         final List<String> columnNames,
                                                         final String schemaName,
                                                         final String tableName) {
    LOGGER.info("Queueing query for table: {}", tableName);
    final AirbyteStreamNameNamespacePair airbyteStream =
        AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.unsafeQuery(
            connection -> createXminQueryStatement(connection, columnNames, schemaName, tableName, airbyteStream),
            sourceOperations::rowToJson);
        return AutoCloseableIterators.fromStream(stream, airbyteStream);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  private PreparedStatement createXminQueryStatement(
                                                     final Connection connection,
                                                     final List<String> columnNames,
                                                     final String schemaName,
                                                     final String tableName,
                                                     final AirbyteStreamNameNamespacePair airbyteStream) {
    try {
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);

      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);

      // Get the xmin status associated with the previous run
      final XminStatus previousRunXminStatus = xminStateManager.getXminStatus(airbyteStream);
      final PreparedStatement xminPreparedStatement =
          getXminPreparedStatement(connection, wrappedColumnNames, fullTableName, previousRunXminStatus, currentXminStatus);
      LOGGER.info("Executing query for table {}: {}", tableName, xminPreparedStatement);
      return xminPreparedStatement;
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private PreparedStatement getXminPreparedStatement(final Connection connection,
                                                     final String wrappedColumnNames,
                                                     final String fullTableName,
                                                     final XminStatus prevRunXminStatus,
                                                     final XminStatus currentXminStatus)
      throws SQLException {

    if (prevRunXminStatus == null) {
      throw new RuntimeException("XminStatus not found for table " + fullTableName + ", should have triggered a full sync via ctid path");
    } else if (isSingleWraparound(prevRunXminStatus, currentXminStatus)) {
      // The xmin state that we save represents the lowest XID that is still in progress. To make sure we
      // don't miss data associated with the current transaction, we have to issue an >=. Because of the
      // wraparound, the changes prior to the
      // end xmin xid value must also be captured.
      LOGGER.info("Detect a single wraparound for {}", fullTableName);
      final String sql = String.format("SELECT %s FROM %s WHERE xmin::text::bigint >= ? OR xmin::text::bigint < ?",
          wrappedColumnNames, fullTableName);
      final PreparedStatement preparedStatement = connection.prepareStatement(sql);
      preparedStatement.setLong(1, prevRunXminStatus.getXminXidValue());
      preparedStatement.setLong(2, currentXminStatus.getXminXidValue());

      return preparedStatement;
    } else {
      // The xmin state that we save represents the lowest XID that is still in progress. To make sure we
      // don't miss data associated with the current transaction, we have to issue an >=
      final String sql = String.format("SELECT %s FROM %s WHERE xmin::text::bigint >= ?",
          wrappedColumnNames, fullTableName);

      final PreparedStatement preparedStatement = connection.prepareStatement(sql.toString());
      preparedStatement.setLong(1, prevRunXminStatus.getXminXidValue());

      return preparedStatement;
    }
  }

  @VisibleForTesting
  static boolean isSingleWraparound(final XminStatus prevRunXminStatus, final XminStatus currentXminStatus) {
    // Detect whether the source Postgres DB has undergone a single wraparound event.
    return currentXminStatus.getNumWraparound() - prevRunXminStatus.getNumWraparound() == 1;
  }

  static boolean shouldPerformFullSync(final XminStatus currentXminStatus, final JsonNode streamState) {
    // Detects whether source Postgres DB has undergone multiple wraparound events between syncs.
    return streamState.has("num_wraparound") && (currentXminStatus.getNumWraparound() - streamState.get("num_wraparound").asLong() >= 2);
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private static AutoCloseableIterator<AirbyteMessage> getRecordIterator(
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
                                                                final AirbyteStreamNameNamespacePair pair,
                                                                final String streamName) {
    final AtomicLong recordCount = new AtomicLong();
    return AutoCloseableIterators.transform(iterator,
        AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()),
        r -> {
          final long count = recordCount.incrementAndGet();
          if (count % 10000 == 0) {
            LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
          }
          return r;
        });
  }

  private AutoCloseableIterator<AirbyteMessage> augmentWithState(final AutoCloseableIterator<AirbyteMessage> recordIterator,
                                                                 final AirbyteStreamNameNamespacePair pair) {
    return AutoCloseableIterators.transform(
        autoCloseableIterator -> new XminStateIterator(
            autoCloseableIterator,
            pair,
            currentXminStatus),
        recordIterator,
        AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()));
  }

}
