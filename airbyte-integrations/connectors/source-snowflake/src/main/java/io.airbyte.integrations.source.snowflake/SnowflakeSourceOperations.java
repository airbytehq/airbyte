/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.math.BigDecimal;
import java.sql.ResultSet;
import java.sql.SQLException;

public class SnowflakeSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putDouble(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) {
    try {
      final double value = resultSet.getDouble(index);
      node.put(columnName, value);
    } catch (final SQLException e) {
      node.put(columnName, (Double) null);
    }
  }

  @Override
  protected void putBigInt(final ObjectNode node, final String columnName, final ResultSet resultSet, int index) {
    try {
      final var value = resultSet.getBigDecimal(index);
      node.put(columnName, value);
    } catch (final SQLException e) {
      node.put(columnName, (BigDecimal) null);
    }
  }

}
