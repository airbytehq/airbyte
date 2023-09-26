/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLDate;
import static io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.commons.json.Jsons;
import java.sql.ResultSet;
import java.sql.SQLException;

public class SnowflakeTestSourceOperations extends JdbcSourceOperations {

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

}
