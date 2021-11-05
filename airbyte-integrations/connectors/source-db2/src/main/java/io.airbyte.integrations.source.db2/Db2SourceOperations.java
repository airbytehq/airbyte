/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Db2SourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(Db2SourceOperations.class);
  private static final List<String> DB2_UNIQUE_NUMBER_TYPES = List.of("DECFLOAT");

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    final int columnCount = queryContext.getMetaData().getColumnCount();
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());

    for (int i = 1; i <= columnCount; i++) {
      setFields(queryContext, i, jsonNode);
    }

    return jsonNode;
  }

  @Override
  protected void setJsonField(ResultSet queryContext, int index, ObjectNode jsonNode) throws SQLException {
    final int columnTypeInt = queryContext.getMetaData().getColumnType(index);
    final String columnName = queryContext.getMetaData().getColumnName(index);
    final JDBCType columnType = safeGetJdbcType(columnTypeInt);

    switch (columnType) {
      case BIT, BOOLEAN -> putBoolean(jsonNode, columnName, queryContext, index);
      case TINYINT, SMALLINT -> putShortInt(jsonNode, columnName, queryContext, index);
      case INTEGER -> putInteger(jsonNode, columnName, queryContext, index);
      case BIGINT -> putBigInt(jsonNode, columnName, queryContext, index);
      case FLOAT, DOUBLE -> putDouble(jsonNode, columnName, queryContext, index);
      case REAL -> putReal(jsonNode, columnName, queryContext, index);
      case NUMERIC, DECIMAL -> putNumber(jsonNode, columnName, queryContext, index);
      case CHAR, VARCHAR, LONGVARCHAR -> putString(jsonNode, columnName, queryContext, index);
      case DATE -> putDate(jsonNode, columnName, queryContext, index);
      case TIME -> putTime(jsonNode, columnName, queryContext, index);
      case TIMESTAMP -> putTimestamp(jsonNode, columnName, queryContext, index);
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(jsonNode, columnName, queryContext, index);
      default -> putDefault(jsonNode, columnName, queryContext, index);
    }
  }

  /* Helpers */

  private void setFields(ResultSet queryContext, int index, ObjectNode jsonNode) throws SQLException {
    try {
      queryContext.getObject(index);
      if (!queryContext.wasNull()) {
        setJsonField(queryContext, index, jsonNode);
      }
    } catch (SQLException e) {
      if (DB2_UNIQUE_NUMBER_TYPES.contains(queryContext.getMetaData().getColumnTypeName(index))) {
        db2UniqueTypes(queryContext, index, jsonNode);
      } else {
        throw new SQLException(e.getCause());
      }
    }
  }

  private void db2UniqueTypes(ResultSet resultSet, int index, ObjectNode jsonNode) throws SQLException {
    String columnType = resultSet.getMetaData().getColumnTypeName(index);
    String columnName = resultSet.getMetaData().getColumnName(index);
    if (DB2_UNIQUE_NUMBER_TYPES.contains(columnType)) {
      putDecfloat(jsonNode, columnName, resultSet, index);
    }
  }

  private void putDecfloat(final ObjectNode node,
                           final String columnName,
                           final ResultSet resultSet,
                           final int index) {
    try {
      final double value = resultSet.getDouble(index);
      node.put(columnName, value);
    } catch (final SQLException e) {
      node.put(columnName, (Double) null);
    }
  }

}
