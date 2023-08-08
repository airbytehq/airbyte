package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlQueryUtils {
  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlQueryUtils.class);
  public record TableSizeInfo(Long tableSize, Long numRows) { }

  public static final String TABLE_ESTIMATE_QUERY =
      """
      SELECT
        (data_length + index_length) as %s, 
        table_rows as %s
     FROM 
        information_schema.tables
     WHERE
        table_schema = %s AND table_name = %s;  
      """;

  public static final String TABLE_SIZE_BYTES_COL = "TotalSizeBytes";
  public static final String TABLE_ROWS_ESTIMATE_COL = "TableRows";

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
        Preconditions.checkState(tableEstimateResult.size() == 1);
        final long tableEstimateBytes = tableEstimateResult.get(0).get(TABLE_SIZE_BYTES_COL).asLong();
        final long tableEstimateRows = tableEstimateResult.get(0).get(TABLE_ROWS_ESTIMATE_COL).asLong();
        LOGGER.info("Stream {} size estimate is {}, row estimate is {}", fullTableName, tableEstimateBytes, tableEstimateRows);
        final TableSizeInfo tableSizeInfo = new TableSizeInfo(tableEstimateBytes, tableEstimateRows);
        final AirbyteStreamNameNamespacePair namespacePair =
            new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
        tableSizeInfoMap.put(namespacePair, tableSizeInfo);
      } catch (final SQLException e) {
        LOGGER.warn("Error occurred while attempting to estimate sync size", e);
      }
    });
    return tableSizeInfoMap;
  }

  private static List<JsonNode> getTableEstimate(final JdbcDatabase database, final String namespace, final String name)
      throws SQLException {
    // Construct the table estimate query.
    final String tableEstimateQuery =
        String.format(TABLE_ESTIMATE_QUERY, TABLE_SIZE_BYTES_COL, TABLE_ROWS_ESTIMATE_COL, namespace, name);
    LOGGER.debug("table estimate query: {}", tableEstimateQuery);
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(tableEstimateQuery),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    return jsonNodes;
  }
}
