/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.commons.json.Jsons;
import java.sql.Array;
import java.sql.ResultSet;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Custom source operations for ClickHouse that handles array types properly without relying on the
 * deprecated getResultSet() method.
 *
 * This class addresses compatibility issues with ClickHouse JDBC driver v0.6.3 where the
 * getResultSet() method for Array objects is no longer implemented.
 *
 * Key features: - Uses Array.getArray() for direct array data access - Provides fallback to string
 * representation for error cases - Maintains compatibility with Airbyte CDK expectations - Supports
 * all ClickHouse array types (Array(String), Array(Int32), etc.)
 *
 * @since 0.2.8
 */
public class ClickHouseSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickHouseSourceOperations.class);

  /**
   * Overrides the default array handling to work with ClickHouse JDBC driver v0.6.3+
   *
   * The default implementation uses Array.getResultSet() which is not implemented in the newer
   * ClickHouse JDBC driver. This method uses Array.getArray() instead which directly returns the
   * array data as a Java array or primitive array.
   *
   * @param node The ObjectNode to add the array data to
   * @param columnName The name of the column being processed
   * @param resultSet The JDBC ResultSet containing the data
   * @param index The 1-based index of the column in the ResultSet
   * @throws SQLException If there's an error accessing the ResultSet data
   */
  @Override
  protected void putArray(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    try {
      final Array array = resultSet.getArray(index);
      if (array != null) {
        // Instead of using getResultSet() which is not implemented in ClickHouse JDBC 0.6.3,
        // we use getArray() which returns the actual array data
        final Object arrayData = array.getArray();
        if (arrayData != null) {
          // Convert the array to a JsonNode and put it in the result
          final JsonNode jsonArray = Jsons.jsonNode(arrayData);
          node.set(columnName, jsonArray);
        } else {
          node.put(columnName, (String) null);
        }
      } else {
        node.put(columnName, (String) null);
      }
    } catch (final SQLException e) {
      LOGGER.warn("Failed to process array for column {}: {}", columnName, e.getMessage());
      // Fallback: try to get it as a string representation
      try {
        final String arrayAsString = resultSet.getString(index);
        node.put(columnName, arrayAsString);
      } catch (final SQLException fallbackException) {
        LOGGER.error("Failed to process array as string for column {}: {}", columnName, fallbackException.getMessage());
        node.put(columnName, (String) null);
      }
    }
  }

}
