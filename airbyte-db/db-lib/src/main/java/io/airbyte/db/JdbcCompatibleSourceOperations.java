/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

public interface JdbcCompatibleSourceOperations<SourceType> extends SourceOperations<ResultSet, SourceType> {

  /**
   * Read from a result set, and copy the value of the column at colIndex to the Json object.
   * <p/>
   *
   * @param colIndex 1-based column index.
   */
  void setJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException;

  /**
   * Set the cursor field in incremental table query.
   */
  void setStatementField(final PreparedStatement preparedStatement,
                         final int parameterIndex,
                         final SourceType cursorFieldType,
                         final String value)
      throws SQLException;

  /**
   * Determine the database specific type of the input field based on its column metadata.
   */
  SourceType getFieldType(final JsonNode field);

  /**
   * @return the input identifiers with quotes and delimiters.
   */
  String enquoteIdentifierList(final Connection connection, final List<String> identifiers) throws SQLException;

  /**
   * @return the input identifier with quotes.
   */
  String enquoteIdentifier(final Connection connection, final String identifier) throws SQLException;

  /**
   * @return fully qualified table name with the schema (if a schema exists).
   */
  String getFullyQualifiedTableName(final String schemaName, final String tableName);

  /**
   * @return fully qualified table name with the schema (if a schema exists) in quotes.
   */
  String getFullyQualifiedTableNameWithQuoting(final Connection connection, final String schemaName, final String tableName) throws SQLException;

  /**
   * This method will verify that filed could be used as cursor for incremental sync
   *
   * @param type - table field type that should be checked
   * @return true is field type can be used as cursor field for incremental sync
   */
  boolean isCursorType(final SourceType type);

}
