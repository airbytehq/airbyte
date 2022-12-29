/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.DateTimeConverter;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTestUtils;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalTime;

public class SnowflakeTestSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putString(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    DestinationAcceptanceTestUtils.putStringIntoJson(resultSet.getString(index), columnName, node);
  }

  @Override
  protected void putTime(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, resultSet.getString(index));
  }

}
