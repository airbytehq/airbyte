/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static io.airbyte.cdk.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;
import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import java.sql.Date;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSourceOperations.class);

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final int columnTypeInt = resultSet.getMetaData().getColumnType(colIndex);
    final String columnName = resultSet.getMetaData().getColumnName(colIndex);
    final JDBCType columnType = safeGetJdbcType(columnTypeInt);

    if ("timestamptz".equalsIgnoreCase(resultSet.getMetaData().getColumnTypeName(colIndex))) {
      // Massive hack. Sometimes the JDBCType is TIMESTAMP (i.e. without timezone)
      // even though it _should_ be TIMESTAMP_WITH_TIMEZONE.
      // Check for this case explicitly.
      putTimestampWithTimezone(json, columnName, resultSet, colIndex);
    } else {
      // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
      switch (columnType) {
        case BIT, BOOLEAN -> putBoolean(json, columnName, resultSet, colIndex);
        case TINYINT, SMALLINT -> putShortInt(json, columnName, resultSet, colIndex);
        case INTEGER -> putInteger(json, columnName, resultSet, colIndex);
        case BIGINT -> putBigInt(json, columnName, resultSet, colIndex);
        case FLOAT, DOUBLE -> putDouble(json, columnName, resultSet, colIndex);
        case REAL -> putFloat(json, columnName, resultSet, colIndex);
        case NUMERIC, DECIMAL -> putBigDecimal(json, columnName, resultSet, colIndex);
        case CHAR, VARCHAR, LONGVARCHAR -> putString(json, columnName, resultSet, colIndex);
        case DATE -> putDate(json, columnName, resultSet, colIndex);
        case TIME -> putTime(json, columnName, resultSet, colIndex);
        case TIMESTAMP -> putTimestamp(json, columnName, resultSet, colIndex);
        case TIMESTAMP_WITH_TIMEZONE -> putTimestampWithTimezone(json, columnName, resultSet, colIndex);
        case BLOB, BINARY, VARBINARY, LONGVARBINARY -> putBinary(json, columnName, resultSet, colIndex);
        case ARRAY -> putArray(json, columnName, resultSet, colIndex);
        default -> putDefault(json, columnName, resultSet, colIndex);
      }
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
  protected void putTimestampWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
      throws SQLException {
    try {
      final OffsetDateTime timestamptz = getObject(resultSet, index, OffsetDateTime.class);
      final LocalDate localDate = timestamptz.toLocalDate();
      node.put(columnName, resolveEra(localDate, timestamptz.format(TIMESTAMPTZ_FORMATTER)));
    } catch (final Exception e) {
      final Instant instant = resultSet.getTimestamp(index).toInstant();
      node.put(columnName, instant.toString());
    }
  }

  @Override
  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    final LocalDate date = LocalDate.parse(value);
    // LocalDate must be converted to java.sql.Date. Please see
    // https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-data-type-mapping.html
    preparedStatement.setDate(parameterIndex, Date.valueOf(date));
  }

}
