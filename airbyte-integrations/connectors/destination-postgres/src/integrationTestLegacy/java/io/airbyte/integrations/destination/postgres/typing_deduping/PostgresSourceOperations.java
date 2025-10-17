/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.commons.json.Jsons;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * See
 * {@link io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGeneratorIntegrationTest.RedshiftSourceOperations}.
 * Copied here to avoid weird dependencies.
 */
public class PostgresSourceOperations extends JdbcSourceOperations {

  @Override
  public void copyToJsonField(final ResultSet resultSet, final int colIndex, final ObjectNode json) throws SQLException {
    final String columnName = resultSet.getMetaData().getColumnName(colIndex);
    final String columnTypeName = resultSet.getMetaData().getColumnTypeName(colIndex).toLowerCase();

    switch (columnTypeName) {
      // JSONB has no equivalent in JDBCType
      case "jsonb" -> json.set(columnName, Jsons.deserializeExact(resultSet.getString(colIndex)));
      // For some reason, the driver maps these to their timezoneless equivalents (TIME and TIMESTAMP)
      case "timetz" -> putTimeWithTimezone(json, columnName, resultSet, colIndex);
      case "timestamptz" -> putTimestampWithTimezone(json, columnName, resultSet, colIndex);
      default -> super.copyToJsonField(resultSet, colIndex, json);
    }
  }

}
