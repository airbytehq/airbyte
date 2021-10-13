/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.ResultSet;
import java.sql.SQLException;

public class MySqlSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putBoolean(ObjectNode node, String columnName, ResultSet resultSet, int index)
      throws SQLException {
    node.put(columnName, resultSet.getInt(index) == 1);
  }

}
