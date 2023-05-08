/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresXminHandler {

  private final JdbcCompatibleSourceOperations sourceOperations;
  private final JdbcDatabase database;
  private final String quoteString;
  private final XminStatus xminStatus;
  private final XminStateManager xminStateManager;

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresXminHandler.class);

  public PostgresXminHandler(final JdbcDatabase database,
                             final JdbcCompatibleSourceOperations sourceOperations,
                             final String quoteString,
                             final XminStatus xminStatus,
                             final List<AirbyteStateMessage> stateMessages) {
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.xminStatus = xminStatus;
    LOGGER.info("State messages from previous run: " + stateMessages);
    this.xminStateManager = new XminStateManager(stateMessages);
  }

  public static boolean isXmin(final JsonNode config) {
    final boolean isXmin = config.hasNonNull("replication_method")
        && config.get("replication_method").get("method").asText().equals("Xmin");
    LOGGER.info("using Xmin: {}", isXmin);
    return isXmin;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {

    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    /*
     * Process each stream : 1. If a stream doesn't exist in the source anymore, skip it. 2. Get the
     * xmin cursor for the stream.
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

      final TableInfo<CommonField<PostgresType>> table = tableNameToTable
          .get(fullyQualifiedTableName);
      final List<String> selectedDatabaseFields = table.getFields()
          .stream()
          .map(CommonField::getName)
          .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains)
          .collect(Collectors.toList());

      final AutoCloseableIterator<JsonNode> queryStream =
          queryTableXmin(selectedDatabaseFields, table.getNameSpace(),
              table.getName());
      final AutoCloseableIterator<AirbyteMessage> airbyteMessageIterator =
          getMessageIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
      final AutoCloseableIterator<AirbyteMessage> iterator;
      iterator = AutoCloseableIterators.transform(
          autoCloseableIterator -> new XminStateIterator(
              autoCloseableIterator,
              stateManager,
              pair,
              xminStatus),
          airbyteMessageIterator,
          AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()));
      iteratorList.add(iterator);
    }

    return iteratorList;
  }

  private AutoCloseableIterator<JsonNode> queryTableXmin(
                                                         final List<String> columnNames,
                                                         final String schemaName,
                                                         final String tableName) {
    LOGGER.info("Queueing query for table: {}", tableName);
    final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair airbyteStream =
        AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.unsafeQuery(
            connection -> {
              LOGGER.info("Preparing query for table: {}", tableName);
              final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
                  quoteString);
              /*
               * final String quotedCursorField = enquoteIdentifier(cursorInfo.getCursorField(),
               * getQuoteString());
               *
               *
               * final String wrappedColumnNames = getWrappedColumnNames(database, connection, columnNames,
               * schemaName, tableName);
               */
              final StringBuilder sql = new StringBuilder(String.format("SELECT * FROM %s WHERE xmin::text::bigint > ?",
                  fullTableName));

              final PreparedStatement preparedStatement = connection.prepareStatement(sql.toString());

              final XminStatus currentStreamXminStatus = xminStateManager.getXminStatus(airbyteStream);
              if (currentStreamXminStatus != null) {
                preparedStatement.setLong(1, currentStreamXminStatus.getXminXidValue());
              } else {
                preparedStatement.setLong(1, 0L);
              }
              LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
              return preparedStatement;
            },
            sourceOperations::rowToJson);
        return AutoCloseableIterators.fromStream(stream, airbyteStream);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    }, airbyteStream);
  }

  public static boolean shouldUseXmin(final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .anyMatch(syncMode -> syncMode == SyncMode.INCREMENTAL);
  }

  private static AutoCloseableIterator<AirbyteMessage> getMessageIterator(
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

}
