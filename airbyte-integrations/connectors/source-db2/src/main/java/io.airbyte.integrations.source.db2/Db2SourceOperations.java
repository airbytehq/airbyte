/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.Date;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;
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

  /* Helpers */

  private void setFields(final ResultSet queryContext, final int index, final ObjectNode jsonNode) throws SQLException {
    try {
      queryContext.getObject(index);
      if (!queryContext.wasNull()) {
        copyToJsonField(queryContext, index, jsonNode);
      }
    } catch (final SQLException e) {
      if (DB2_UNIQUE_NUMBER_TYPES.contains(queryContext.getMetaData().getColumnTypeName(index))) {
        db2UniqueTypes(queryContext, index, jsonNode);
      } else {
        throw new SQLException(e.getCause());
      }
    }
  }

  private void db2UniqueTypes(final ResultSet resultSet, final int index, final ObjectNode jsonNode) throws SQLException {
    final String columnType = resultSet.getMetaData().getColumnTypeName(index);
    final String columnName = resultSet.getMetaData().getColumnName(index);
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

  @Override
  protected void putTime(final ObjectNode node,
                         final String columnName,
                         final ResultSet resultSet,
                         final int index)
      throws SQLException {
    putJavaSQLTime(node, columnName, resultSet, index);
  }

  @Override
  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final Timestamp timestamp = resultSet.getTimestamp(index);
    node.put(columnName, DateTimeConverter.convertToTimestamp(timestamp));
  }

  @Override
  protected void setTimestamp(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    final LocalDateTime date = LocalDateTime.parse(value);
    preparedStatement.setTimestamp(parameterIndex, Timestamp.valueOf(date));
  }

  @Override
  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    final LocalDate date = LocalDate.parse(value);
    preparedStatement.setDate(parameterIndex, Date.valueOf(date));
  }

  @Override
  public JsonSchemaType getAirbyteType(final JDBCType jdbcType) {
    switch (jdbcType) {
      case SMALLINT, INTEGER, BIGINT:
        return JsonSchemaType.INTEGER;
      case DOUBLE, DECIMAL, NUMERIC, REAL:
        return JsonSchemaType.NUMBER;
      case DATE:
        return JsonSchemaType.STRING_DATE;
      case BLOB, BINARY, VARBINARY:
        return JsonSchemaType.STRING_BASE_64;
      case TIME:
        return JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE;
      case TIMESTAMP:
        return JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
      default:
        return super.getAirbyteType(jdbcType);
    }
  }

}
