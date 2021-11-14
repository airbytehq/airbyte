/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import io.airbyte.commons.functional.CheckedFunction;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;

public interface JdbcCompatibleSourceOperations<SourceType> extends SourceOperations<ResultSet, SourceType> {

  void setStatementField(final PreparedStatement preparedStatement,
                         final int parameterIndex,
                         final SourceType cursorFieldType,
                         final String value)
      throws SQLException;

  /**
   * Map records returned in a result set.
   *
   * @param resultSet the result set
   * @param mapper function to make each record of the result set
   * @param <T> type that each record will be mapped to
   * @return stream of records that the result set is mapped to.
   */
  <T> Stream<T> toStream(final ResultSet resultSet, final CheckedFunction<ResultSet, T, SQLException> mapper);

  String enquoteIdentifierList(final Connection connection, final List<String> identifiers) throws SQLException;

  String enquoteIdentifier(final Connection connection, final String identifier) throws SQLException;

  String getFullyQualifiedTableName(final String schemaName, final String tableName);

  String getFullyQualifiedTableNameWithQuoting(final Connection connection, final String schemaName, final String tableName) throws SQLException;

}
