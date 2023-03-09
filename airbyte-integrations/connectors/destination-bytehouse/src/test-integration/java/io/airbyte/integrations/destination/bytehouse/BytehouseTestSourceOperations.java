/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bytehouse;

import io.airbyte.db.jdbc.JdbcSourceOperations;

public class BytehouseTestSourceOperations extends JdbcSourceOperations {

  // @Override
  // protected void putDate(final ObjectNode node, final String columnName, final ResultSet resultSet,
  // final int index) throws SQLException {
  // node.put(columnName,
  // DateTimeFormatter.ISO_DATE.format(resultSet.getTimestamp(index).toLocalDateTime()));
  // }
  //
  // @Override
  // protected void putTimestamp(final ObjectNode node, final String columnName, final ResultSet
  // resultSet, final int index) throws SQLException {
  // final LocalDateTime timestamp = getObject(resultSet, index, LocalDateTime.class);
  // final LocalDate date = timestamp.toLocalDate();
  //
  // DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern(
  // DataTypeUtils.DATE_FORMAT_WITH_MILLISECONDS_PATTERN);
  //
  // node.put(columnName, resolveEra(date, timestamp.format(dateTimeFormatter)));
  // }

}
