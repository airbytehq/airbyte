/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

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

}
