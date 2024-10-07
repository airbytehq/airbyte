/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSourceOperations.class);

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    if ("timestamptz".equalsIgnoreCase(resultSet.getMetaData().getColumnTypeName(colIndex))) {
      // Massive hack. Sometimes the JDBCType is TIMESTAMP (i.e. without timezone)
      // even though it _should_ be TIMESTAMP_WITH_TIMEZONE.
      // Check for this case explicitly.
      final String columnName = resultSet.getMetaData().getColumnName(colIndex);
      putTimestampWithTimezone(json, columnName, resultSet, colIndex);
    } else {
      super.copyToJsonField(resultSet, colIndex, json);
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
      super.putTimestampWithTimezone(node, columnName, resultSet, index);
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
