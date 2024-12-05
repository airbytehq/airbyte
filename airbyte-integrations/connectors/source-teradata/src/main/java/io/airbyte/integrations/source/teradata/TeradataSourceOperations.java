/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata;

import static io.airbyte.cdk.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.DataTypeUtils;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Time;
import java.sql.Timestamp;
import java.text.ParseException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.OffsetTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeParseException;

// Teradata only supports native java.sql types when creating prepared statements and returning from
// resultSet
public class TeradataSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putDate(ObjectNode node, String columnName, ResultSet resultSet, int index)
      throws SQLException {
    Object obj = resultSet.getObject(index);
    node.put(columnName, DateTimeConverter.convertToDate(obj));
  }

  @Override
  protected void putTime(ObjectNode node, String columnName, ResultSet resultSet, int index)
      throws SQLException {
    Object obj = resultSet.getObject(index);
    node.put(columnName, DateTimeConverter.convertToTime(obj));
  }

  @Override
  protected void putTimestamp(ObjectNode node,
                              String columnName,
                              ResultSet resultSet,
                              int index)
      throws SQLException {
    Timestamp timestamp = (Timestamp) resultSet.getObject(index);
    node.put(columnName, DataTypeUtils.toISO8601StringWithMicroseconds(timestamp.toInstant()));
  }

  @Override
  protected void putTimestampWithTimezone(ObjectNode node,
                                          String columnName,
                                          ResultSet resultSet,
                                          int index)
      throws SQLException {
    Timestamp timestamp = (Timestamp) resultSet.getObject(index);
    final OffsetDateTime timestamptz = timestamp.toLocalDateTime().atOffset(ZoneOffset.UTC);
    final LocalDate localDate = timestamptz.toLocalDate();
    node.put(columnName, resolveEra(localDate, timestamptz.format(TIMESTAMPTZ_FORMATTER)));
  }

  @Override
  protected void setDate(PreparedStatement preparedStatement, int parameterIndex, String value)
      throws SQLException {
    try {
      // LocalDate is unsupported by the Teradata driver if provided directly
      preparedStatement.setObject(parameterIndex, Date.valueOf(LocalDate.parse(value)));
    } catch (final DateTimeParseException dtpe) {
      try {
        final Timestamp from = Timestamp.from(DataTypeUtils.getDateFormat().parse(value).toInstant());
        preparedStatement.setDate(parameterIndex, new Date(from.getTime()));
      } catch (final ParseException pe) {
        throw new RuntimeException(pe);
      }
    }
  }

  @Override
  protected void setTime(PreparedStatement preparedStatement, int parameterIndex, String value)
      throws SQLException {
    try {
      // LocalTime is unsupported by the Teradata driver if provided directly
      preparedStatement.setObject(parameterIndex, Time.valueOf(LocalTime.parse(value)));
    } catch (final DateTimeParseException e) {
      setTimestamp(preparedStatement, parameterIndex, value);
    }
  }

  @Override
  protected void setTimestamp(PreparedStatement preparedStatement, int parameterIndex, String value)
      throws SQLException {
    try {
      preparedStatement.setObject(parameterIndex, Timestamp.valueOf(LocalDateTime.parse(value)));
    } catch (final DateTimeParseException e) {
      preparedStatement.setObject(parameterIndex, Timestamp.valueOf(OffsetDateTime.parse(value).toLocalDateTime()));
    }
  }

  @Override
  protected void setTimeWithTimezone(PreparedStatement preparedStatement,
                                     int parameterIndex,
                                     String value)
      throws SQLException {
    try {
      preparedStatement.setObject(parameterIndex, Time.valueOf(OffsetTime.parse(value).toLocalTime()));
    } catch (final DateTimeParseException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void setTimestampWithTimezone(PreparedStatement preparedStatement,
                                          int parameterIndex,
                                          String value)
      throws SQLException {
    try {
      preparedStatement.setObject(parameterIndex, Timestamp.valueOf(OffsetDateTime.parse(value).toLocalDateTime()));
    } catch (final DateTimeParseException e) {
      throw new RuntimeException(e);
    }
  }

}
