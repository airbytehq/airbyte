/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLDate;
import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.DataTypeUtils;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.commons.json.Jsons;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;

public class SnowflakeSourceOperations extends JdbcSourceOperations {

  private static final DateTimeFormatter SNOWFLAKE_TIMESTAMPTZ_FORMATTER = new DateTimeFormatterBuilder()
      .parseCaseInsensitive()
      .append(DateTimeFormatter.ISO_LOCAL_DATE)
      .appendLiteral(' ')
      .append(DateTimeFormatter.ISO_LOCAL_TIME)
      .optionalStart()
      .appendLiteral(' ')
      .append(DateTimeFormatter.ofPattern("XX"))
      .toFormatter();

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final String columnName = resultSet.getMetaData().getColumnName(colIndex);
    final String columnTypeName = resultSet.getMetaData().getColumnTypeName(colIndex).toLowerCase();

    switch (columnTypeName) {
      // jdbc converts VARIANT columns to serialized JSON, so we need to deserialize these.
      case "variant", "array", "object" -> json.set(columnName, Jsons.deserializeExact(resultSet.getString(colIndex)));
      default -> super.copyToJsonField(resultSet, colIndex, json);
    }
  }

  @Override
  protected void putDate(final ObjectNode node,
                         final String columnName,
                         final ResultSet resultSet,
                         final int index)
      throws SQLException {
    putJavaSQLDate(node, columnName, resultSet, index);
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
  protected void putTimestampWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
      throws SQLException {
    final String timestampAsString = resultSet.getString(index);
    OffsetDateTime timestampWithOffset = OffsetDateTime.parse(timestampAsString, SNOWFLAKE_TIMESTAMPTZ_FORMATTER);
    node.put(columnName, timestampWithOffset.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER));
  }

  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    // for backward compatibility
    var instant = resultSet.getTimestamp(index).toInstant();
    node.put(columnName, DataTypeUtils.toISO8601StringWithMicroseconds(instant));
  }

}
