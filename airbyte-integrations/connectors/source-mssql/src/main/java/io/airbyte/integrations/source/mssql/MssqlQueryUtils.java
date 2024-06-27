/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifierList;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getIdentifierWithQuoting;
import static io.airbyte.integrations.source.mssql.MssqlSource.HIERARCHYID;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import com.microsoft.sqlserver.jdbc.SQLServerResultSetMetaData;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.cdk.integrations.source.relationaldb.models.CursorBasedStatus;
import io.airbyte.cdk.integrations.source.relationaldb.models.InternalModels.StateType;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.math.BigDecimal;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to define constants related to querying mssql
 */
public class MssqlQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlQueryUtils.class);
  private static final String MAX_OC_VALUE_QUERY =
      """
        SELECT MAX(%s) as %s FROM %s;
      """;

  public record TableSizeInfo(Long tableSize, Long avgRowLength) {}

  private static final String MAX_CURSOR_VALUE_QUERY =
      """
        SELECT TOP 1 %s, COUNT(*) AS %s FROM %s WHERE %s = (SELECT MAX(%s) FROM %s) GROUP BY %s;
      """;
  public static final String INDEX_QUERY = "EXEC sp_helpindex N'%s'";

  public record Index(
                      @JsonProperty("index_name") String name,
                      @JsonProperty("index_description") String description,
                      @JsonProperty("index_keys") String keys) {}

  public static final String TABLE_ESTIMATE_QUERY =
      """
      EXEC sp_spaceused N'"%s"."%s"'
      """;

  public static final String MAX_OC_COL = "max_oc";
  public static final String DATA_SIZE_HUMAN_READABLE = "data";
  public static final String NUM_ROWS = "rows";

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
              .forEach(i -> LOGGER.info("Index {}", i));
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

  private static long toBytes(final String filesize) {
    long returnValue = -1;
    final Pattern patt = Pattern.compile("([\\d.]+)[\s+]*([GMK]B)", Pattern.CASE_INSENSITIVE);
    final Matcher matcher = patt.matcher(filesize);
    Map<String, Integer> powerMap = new HashMap<String, Integer>();
    powerMap.put("GB", 3);
    powerMap.put("MB", 2);
    powerMap.put("KB", 1);
    if (matcher.find()) {
      String number = matcher.group(1).trim();
      int pow = powerMap.get(matcher.group(2).toUpperCase());
      BigDecimal bytes = new BigDecimal(number);
      bytes = bytes.multiply(BigDecimal.valueOf(1024).pow(pow));
      returnValue = bytes.longValue();
    }
    return returnValue;
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
            && tableEstimateResult.get(0).get(DATA_SIZE_HUMAN_READABLE) != null
            && tableEstimateResult.get(0).get(NUM_ROWS) != null) {
          final long tableEstimateBytes = toBytes(tableEstimateResult.get(0).get(DATA_SIZE_HUMAN_READABLE).asText());
          final long numRows = tableEstimateResult.get(0).get(NUM_ROWS).asLong();
          final long avgTableRowSizeBytes = numRows > 0 ? tableEstimateBytes / numRows : 0;
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

  /**
   * Iterates through each stream and find the max cursor value and the record count which has that
   * value based on each cursor field provided by the customer per stream This information is saved in
   * a Hashmap with the mapping being the AirbyteStreamNameNamespacepair -> CursorBasedStatus
   *
   * @param database the source db
   * @param streams streams to be synced
   * @param stateManager stream stateManager
   * @return Map of streams to statuses
   */
  public static Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, CursorBasedStatus> getCursorBasedSyncStatusForStreams(final JdbcDatabase database,
                                                                                                                                        final List<ConfiguredAirbyteStream> streams,
                                                                                                                                        final StateManager stateManager,
                                                                                                                                        final String quoteString) {

    final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, CursorBasedStatus> cursorBasedStatusMap = new HashMap<>();
    streams.forEach(stream -> {
      final String name = stream.getStream().getName();
      final String namespace = stream.getStream().getNamespace();
      final String fullTableName =
          getFullyQualifiedTableNameWithQuoting(namespace, name, quoteString);

      final Optional<CursorInfo> cursorInfoOptional =
          stateManager.getCursorInfo(new AirbyteStreamNameNamespacePair(name, namespace));
      if (cursorInfoOptional.isEmpty()) {
        throw new RuntimeException(String.format("Stream %s was not provided with an appropriate cursor", stream.getStream().getName()));
      }
      final CursorBasedStatus cursorBasedStatus = new CursorBasedStatus();
      final Optional<String> maybeCursorField = Optional.ofNullable(cursorInfoOptional.get().getCursorField());
      maybeCursorField.ifPresent(cursorField -> {
        LOGGER.info("Cursor {}. Querying max cursor value for {}.{}", cursorField, namespace, name);
        final String quotedCursorField = getIdentifierWithQuoting(cursorField, quoteString);
        final String counterField = cursorField + "_count";
        final String quotedCounterField = getIdentifierWithQuoting(counterField, quoteString);
        final String cursorBasedSyncStatusQuery = String.format(MAX_CURSOR_VALUE_QUERY,
            quotedCursorField,
            quotedCounterField,
            fullTableName,
            quotedCursorField,
            quotedCursorField,
            fullTableName,
            quotedCursorField);
        final List<JsonNode> jsonNodes;
        try {
          jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(cursorBasedSyncStatusQuery).executeQuery(),
              resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
        } catch (SQLException e) {
          throw new RuntimeException("Failed to read max cursor value from %s.%s".formatted(namespace, name), e);
        }
        cursorBasedStatus.setCursorField(ImmutableList.of(cursorField));
        if (!jsonNodes.isEmpty()) {
          final JsonNode result = jsonNodes.get(0);
          cursorBasedStatus.setCursor(result.get(cursorField).asText());
          cursorBasedStatus.setCursorRecordCount(result.get(counterField).asLong());
        }
        cursorBasedStatus.setStateType(StateType.CURSOR_BASED);
        cursorBasedStatus.setVersion(2L);
        cursorBasedStatus.setStreamName(name);
        cursorBasedStatus.setStreamNamespace(namespace);
        cursorBasedStatusMap.put(new AirbyteStreamNameNamespacePair(name, namespace), cursorBasedStatus);
      });
    });

    return cursorBasedStatusMap;
  }

  private static List<JsonNode> getTableEstimate(final JdbcDatabase database, final String namespace, final String name)
      throws SQLException {
    // Construct the table estimate query.
    final String tableEstimateQuery =
        String.format(TABLE_ESTIMATE_QUERY, namespace, name);
    LOGGER.info("Querying for table estimate size: {}", tableEstimateQuery);
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(tableEstimateQuery),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    LOGGER.debug("Estimate: {}", jsonNodes);
    return jsonNodes;
  }

  public static String prettyPrintConfiguredAirbyteStreamList(final List<ConfiguredAirbyteStream> streamList) {
    return streamList.stream().map(s -> "%s.%s".formatted(s.getStream().getNamespace(), s.getStream().getName())).collect(Collectors.joining(", "));
  }

  /**
   * There is no support for hierarchyid even in the native SQL Server JDBC driver. Its value can be
   * converted to a nvarchar(4000) data type by calling the ToString() method. So we make a separate
   * query to get Table's MetaData, check is there any hierarchyid columns, and wrap required fields
   * with the ToString() function in the final Select query. Reference:
   * https://docs.microsoft.com/en-us/sql/t-sql/data-types/hierarchyid-data-type-method-reference?view=sql-server-ver15#data-type-conversion
   * Note: This is where the main logic for the same method in MssqlSource. Extracted logic in order
   * to be used in MssqlInitialLoadRecordIterator
   *
   * @return the list with Column names updated to handle functions (if nay) properly
   */
  public static String getWrappedColumnNames(
                                             final JdbcDatabase database,
                                             final String quoteString,
                                             final List<String> columnNames,
                                             final String schemaName,
                                             final String tableName) {
    final List<String> hierarchyIdColumns = new ArrayList<>();
    try {
      final String identifierQuoteString = database.getMetaData().getIdentifierQuoteString();
      final SQLServerResultSetMetaData sqlServerResultSetMetaData = (SQLServerResultSetMetaData) database
          .queryMetadata(String
              .format("SELECT TOP 1 %s FROM %s", // only first row is enough to get field's type
                  enquoteIdentifierList(columnNames, quoteString),
                  getFullyQualifiedTableNameWithQuoting(schemaName, tableName, quoteString)));

      // metadata will be null if table doesn't contain records
      if (sqlServerResultSetMetaData != null) {
        for (int i = 1; i <= sqlServerResultSetMetaData.getColumnCount(); i++) {
          if (HIERARCHYID.equals(sqlServerResultSetMetaData.getColumnTypeName(i))) {
            hierarchyIdColumns.add(sqlServerResultSetMetaData.getColumnName(i));
          }
        }
      }

      // iterate through names and replace Hierarchyid field for query is with toString() function
      // Eventually would get columns like this: testColumn.toString as "testColumn"
      // toString function in SQL server is the only way to get human-readable value, but not mssql
      // specific HEX value
      return String.join(", ", columnNames.stream()
          .map(
              el -> hierarchyIdColumns.contains(el) ? String.format("%s.ToString() as %s%s%s", el, identifierQuoteString, el, identifierQuoteString)
                  : getIdentifierWithQuoting(el, quoteString))
          .toList());
    } catch (final SQLException e) {
      LOGGER.error("Failed to fetch metadata to prepare a proper request.", e);
      throw new RuntimeException(e);
    }
  }

}
