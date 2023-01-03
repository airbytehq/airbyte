/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public interface JdbcCompatibleSourceOperations<SourceType> extends SourceOperations<ResultSet, SourceType> {

  /**
   * Read from a result set, and copy the value of the column at colIndex to the Json object.
   * <p/>
   *
   * @param colIndex 1-based column index.
   */
  void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException;

  /**
   * Set the cursor field in incremental table query.
   */
  void setCursorField(final PreparedStatement preparedStatement,
                      final int parameterIndex,
                      final SourceType cursorFieldType,
                      final String value)
      throws SQLException;

  /**
   * Determine the database specific type of the input field based on its column metadata.
   */
  SourceType getDatabaseFieldType(final JsonNode field);

  /**
   * This method will verify that filed could be used as cursor for incremental sync
   *
   * @param type - table field type that should be checked
   * @return true is field type can be used as cursor field for incremental sync
   */
  boolean isCursorType(final SourceType type);

}
