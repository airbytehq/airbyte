/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.format.DateTimeParseException;
import java.util.Calendar;
import java.util.TimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSourceOperations.class);

  // Redshift's default timestamp rendering is e.g. "2026-06-04 05:50:52.815018".
  private static final DateTimeFormatter REDSHIFT_LOCAL_DATETIME = new DateTimeFormatterBuilder()
      .append(DateTimeFormatter.ISO_LOCAL_DATE)
      .appendLiteral(' ')
      .append(DateTimeFormatter.ISO_LOCAL_TIME)
      .toFormatter();

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
    // The Redshift JDBC driver applies a DST-sensitive offset when materializing timestamp values
    // via getTimestamp(), so values can come back shifted by an hour. Read the raw server-rendered
    // string instead (e.g. "2026-06-04 05:50:52.815018") and parse it ourselves.
    final String raw = resultSet.getString(index);
    if (raw == null) {
      return;
    }
    final LocalDateTime timestamp = REDSHIFT_LOCAL_DATETIME.parse(raw, LocalDateTime::from);
    node.put(columnName, DateTimeConverter.convertToTimestamp(timestamp));
  }

  @Override
  protected void setTimestamp(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    try {
      preparedStatement.setTimestamp(parameterIndex, Timestamp.valueOf(LocalDateTime.parse(value)));
    } catch (final DateTimeParseException e) {
      // Fallback: parse timezone-aware timestamps (e.g. "2026-03-11T17:05:58Z").
      // Redshift may report timestamptz columns, whose serialized cursor values
      // contain a UTC offset or 'Z' suffix that LocalDateTime.parse cannot handle.
      preparedStatement.setTimestamp(parameterIndex, Timestamp.from(OffsetDateTime.parse(value).toInstant()));
    }
  }

  @Override
  protected void putTimestampWithTimezone(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index)
      throws SQLException {
    // Do NOT call resultSet.getString(index) for timestamptz columns: the Redshift
    // JDBC driver (1.2.43.1067) internally invokes PGTimestamp.toString() which
    // triggers infinite mutual recursion, causing StackOverflowError.
    // Use the CDK base implementation (getObject → OffsetDateTime) as primary path;
    // fall back to getTimestamp() with a UTC calendar for driver versions where
    // getObject(OffsetDateTime) is unsupported.
    try {
      super.putTimestampWithTimezone(node, columnName, resultSet, index);
    } catch (final Exception e) {
      final Calendar utcCal = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
      final Timestamp ts = resultSet.getTimestamp(index, utcCal);
      if (ts == null) {
        return;
      }
      final OffsetDateTime timestamptz = ts.toInstant().atOffset(ZoneOffset.UTC);
      node.put(columnName, DateTimeConverter.convertToTimestampWithTimezone(timestamptz));
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
