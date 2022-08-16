/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class ClickhouseTestSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putDate(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DateTimeFormatter.ISO_DATE.format(resultSet.getTimestamp(index).toLocalDateTime()));
  }

  @Override
  protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final LocalDateTime timestamp = getObject(resultSet, index, LocalDateTime.class);
    final LocalDate date = timestamp.toLocalDate();

    DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(
        DataTypeUtils.DATE_FORMAT_WITH_MILLISECONDS_PATTERN);

    node.put(columnName, resolveEra(date, timestamp.format(dateTimeFormatter)));
  }

}
