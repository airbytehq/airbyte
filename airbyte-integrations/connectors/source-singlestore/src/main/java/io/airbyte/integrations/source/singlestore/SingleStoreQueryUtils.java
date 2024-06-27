/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getIdentifierWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.singlestore.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.singlestore.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreQueryUtils.class);

  public static final String MAX_PK_VALUE_QUERY = """
                                                    SELECT MAX(%s) as %s FROM %s;
                                                  """;
  public static final String MAX_CURSOR_VALUE_QUERY = """
                                                        SELECT %s FROM %s WHERE %s = (SELECT MAX(%s) FROM %s);
                                                      """;

  public static final String MAX_PK_COL = "max_pk";

  public static String getMaxPkValueForStream(final JdbcDatabase database,
                                              final ConfiguredAirbyteStream stream,
                                              final String pkFieldName,
                                              final String quoteString) {
    final String name = stream.getStream().getName();
    final String namespace = stream.getStream().getNamespace();
    final String fullTableName = getFullyQualifiedTableNameWithQuoting(namespace, name, quoteString);
    final String maxPkQuery = String.format(MAX_PK_VALUE_QUERY, getIdentifierWithQuoting(pkFieldName, quoteString), MAX_PK_COL, fullTableName);
    LOGGER.info("Querying for max pk value: {}", maxPkQuery);
    try {
      final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(maxPkQuery).executeQuery(),
          JdbcUtils.getDefaultSourceOperations()::rowToJson);
      Preconditions.checkState(jsonNodes.size() == 1);
      if (jsonNodes.get(0).get(MAX_PK_COL) == null) {
        LOGGER.info("Max PK is null for table {} - this could indicate an empty table", fullTableName);
        return null;
      }
      return jsonNodes.get(0).get(MAX_PK_COL).asText();
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Iterates through each stream and find the max cursor value and the record count which has that
   * value based on each cursor field provided by the customer per stream. This information is saved
   * in a Hashmap with the mapping being the AirbyteStreamNameNamespacePair -> CursorBasedStatus.
   *
   * @param database the source db
   * @param streams streams to be synced
   * @param stateManager stream stateManager
   * @return Map of streams to statuses
   */
  public static Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, CursorBasedStatus> getCursorBasedSyncStatusForStreams(
                                                                                                                                        final JdbcDatabase database,
                                                                                                                                        final List<ConfiguredAirbyteStream> streams,
                                                                                                                                        final StateManager stateManager,
                                                                                                                                        final String quoteString) {

    final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, CursorBasedStatus> cursorBasedStatusMap = new HashMap<>();
    streams.forEach(stream -> {
      try {
        final String name = stream.getStream().getName();
        final String namespace = stream.getStream().getNamespace();
        final String fullTableName = getFullyQualifiedTableNameWithQuoting(namespace, name, quoteString);

        final Optional<CursorInfo> cursorInfoOptional = stateManager.getCursorInfo(
            new io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(name, namespace));
        if (cursorInfoOptional.isEmpty()) {
          throw new RuntimeException(String.format("Stream %s was not provided with an appropriate cursor", stream.getStream().getName()));
        }

        LOGGER.info("Querying max cursor value for {}.{}", namespace, name);
        final String cursorField = cursorInfoOptional.get().getCursorField();
        final String quotedCursorField = getIdentifierWithQuoting(cursorField, quoteString);
        final String cursorBasedSyncStatusQuery = String.format(MAX_CURSOR_VALUE_QUERY, quotedCursorField, fullTableName, quotedCursorField,
            quotedCursorField, fullTableName);
        final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(cursorBasedSyncStatusQuery).executeQuery(),
            JdbcUtils.getDefaultSourceOperations()::rowToJson);
        final CursorBasedStatus cursorBasedStatus = new CursorBasedStatus();
        cursorBasedStatus.setStateType(StateType.CURSOR_BASED);
        cursorBasedStatus.setStreamName(name);
        cursorBasedStatus.setStreamNamespace(namespace);
        cursorBasedStatus.setCursorField(ImmutableList.of(cursorField));
        if (!jsonNodes.isEmpty()) {
          final JsonNode result = jsonNodes.get(0);
          cursorBasedStatus.setCursor(result.get(cursorField).asText());
          cursorBasedStatus.setCursorRecordCount((long) jsonNodes.size());
        }
        cursorBasedStatusMap.put(new io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(name, namespace), cursorBasedStatus);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    });

    return cursorBasedStatusMap;
  }

  public static void logStreamSyncStatus(final List<ConfiguredAirbyteStream> streams, final String syncType) {
    if (streams.isEmpty()) {
      LOGGER.info("No Streams will be synced via {}.", syncType);
    } else {
      LOGGER.info("Streams to be synced via {} : {}", syncType, streams.size());
      LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(streams));
    }
  }

  public static String prettyPrintConfiguredAirbyteStreamList(final List<ConfiguredAirbyteStream> streamList) {
    return streamList.stream().map(s -> "%s.%s".formatted(s.getStream().getNamespace(), s.getStream().getName())).collect(Collectors.joining(", "));
  }

}
