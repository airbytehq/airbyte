/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;

public interface JdbcCompatibleSourceOperations<SourceType> extends SourceOperations<ResultSet, SourceType> {

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

}
