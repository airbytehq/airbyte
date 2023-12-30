/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getIdentifierWithQuoting;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to define constants related to querying mssql
 */
public class MssqlQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlQueryUtils.class);

  public record TableSizeInfo(Long tableSize, Long avgRowLength) {}
  public static final String INDEX_QUERY = "EXEC sp_helpindex N'%s'";
  public record Index(
      @JsonProperty("index_name") String name,
      @JsonProperty("index_description") String description,
      @JsonProperty("index_keys") String keys
  ) { }

  public static final String TABLE_ESTIMATE_QUERY = """
                                                     SELECT
                                                       (data_length + index_length) as %s,
                                                       AVG_ROW_LENGTH as %s
                                                    FROM
                                                       information_schema.tables
                                                    WHERE
                                                       table_schema = '%s' AND table_name = '%s';
                                                    """;

  public static final String MAX_OC_VALUE_QUERY =
      """
        SELECT MAX(%s) as %s FROM %s;
      """;

  public static final String MAX_OC_COL = "max_oc";
  public static final String TABLE_SIZE_BYTES_COL = "TotalSizeBytes";
  public static final String AVG_ROW_LENGTH = "AVG_ROW_LENGTH";

  public static void getIndexInfoForStreams(final JdbcDatabase database, final ConfiguredAirbyteCatalog catalog, final String quoteString) {
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = stream.getStream().getNamespace();
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, streamName, quoteString);
      LOGGER.info("Discovering indexes for table {}", fullTableName);
      try {
        final String query = INDEX_QUERY.formatted(fullTableName);
        LOGGER.debug("Index lookup query: {}", query);
        final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(query).executeQuery(),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
        if (jsonNodes != null) {
          jsonNodes.stream().map(node -> Jsons.convertValue(node, Index.class))
              .forEach(i -> LOGGER.info(String.valueOf(i)));
        }
      } catch (final Exception ex) {
        LOGGER.info("Failed to get index for {}", fullTableName);
      }
    }

  }

  public static String getMaxOcValueForStream(final JdbcDatabase database,
  final ConfiguredAirbyteStream stream,
  final String ocFieldName,
  final String quoteString) {
    final String name = stream.getStream().getName();
    final String namespace = stream.getStream().getNamespace();
    final String fullTableName =
        getFullyQualifiedTableNameWithQuoting(namespace, name, quoteString);
    final String maxOcQuery = String.format(MAX_OC_VALUE_QUERY,
        getIdentifierWithQuoting(ocFieldName, quoteString),
        MAX_OC_COL,
        fullTableName);
    LOGGER.info("Querying for max oc value: {}", maxOcQuery);
    try {
      final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(maxOcQuery).executeQuery(),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
      Preconditions.checkState(jsonNodes.size() == 1);
      if (jsonNodes.get(0).get(MAX_OC_COL) == null) {
        LOGGER.info("Max PK is null for table {} - this could indicate an empty table", fullTableName);
        return null;
      }
      return jsonNodes.get(0).get(MAX_OC_COL).asText();
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  public static Map<AirbyteStreamNameNamespacePair, TableSizeInfo> getTableSizeInfoForStreams(final JdbcDatabase database,
      final List<ConfiguredAirbyteStream> streams,
      final String quoteString) {
    final Map<AirbyteStreamNameNamespacePair, TableSizeInfo> tableSizeInfoMap = new HashMap<>();
    streams.forEach(stream -> {
      try {
        final String name = stream.getStream().getName();
        final String namespace = stream.getStream().getNamespace();
        final String fullTableName =
            getFullyQualifiedTableNameWithQuoting(name, namespace, quoteString);
        final List<JsonNode> tableEstimateResult = getTableEstimate(database, namespace, name);

        if (tableEstimateResult != null
            && tableEstimateResult.size() == 1
            && tableEstimateResult.get(0).get(TABLE_SIZE_BYTES_COL) != null
            && tableEstimateResult.get(0).get(AVG_ROW_LENGTH) != null) {
          final long tableEstimateBytes = tableEstimateResult.get(0).get(TABLE_SIZE_BYTES_COL).asLong();
          final long avgTableRowSizeBytes = tableEstimateResult.get(0).get(AVG_ROW_LENGTH).asLong();
          LOGGER.info("Stream {} size estimate is {}, average row size estimate is {}", fullTableName, tableEstimateBytes, avgTableRowSizeBytes);
          final TableSizeInfo tableSizeInfo = new TableSizeInfo(tableEstimateBytes, avgTableRowSizeBytes);
          final AirbyteStreamNameNamespacePair namespacePair =
              new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
          tableSizeInfoMap.put(namespacePair, tableSizeInfo);
        }
      } catch (final Exception e) {
        LOGGER.warn("Error occurred while attempting to estimate sync size", e);
      }
    });
    return tableSizeInfoMap;
  }

  private static List<JsonNode> getTableEstimate(final JdbcDatabase database, final String namespace, final String name)
      throws SQLException {
    // Construct the table estimate query.
    final String tableEstimateQuery =
        String.format(TABLE_ESTIMATE_QUERY, TABLE_SIZE_BYTES_COL, AVG_ROW_LENGTH, namespace, name);
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(tableEstimateQuery),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    return jsonNodes;
  }

  public static String prettyPrintConfiguredAirbyteStreamList(final List<ConfiguredAirbyteStream> streamList) {
    return streamList.stream().map(s -> "%s.%s".formatted(s.getStream().getNamespace(), s.getStream().getName())).collect(Collectors.joining(", "));
  }

}
