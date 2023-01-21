/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.db.jdbc.DateTimeConverter.putJavaSQLDate;
import static io.airbyte.db.jdbc.DateTimeConverter.putJavaSQLTime;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTestUtils;
import java.sql.ResultSet;
import java.sql.SQLException;

public class SnowflakeTestSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putString(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    DestinationAcceptanceTestUtils.putStringIntoJson(resultSet.getString(index), columnName, node);
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

}
