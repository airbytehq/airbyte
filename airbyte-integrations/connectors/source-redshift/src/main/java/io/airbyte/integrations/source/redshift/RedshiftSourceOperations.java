/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static io.airbyte.db.jdbc.DateTimeConverter.putJavaSQLDate;
import static io.airbyte.db.jdbc.DateTimeConverter.putJavaSQLTime;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSourceOperations.class);

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

  @Override
  protected void setDate(final PreparedStatement preparedStatement, final int parameterIndex, final String value) throws SQLException {
    final LocalDate date = LocalDate.parse(value);
    // LocalDate must be converted to java.sql.Date. Please see
    // https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-data-type-mapping.html
    preparedStatement.setDate(parameterIndex, Date.valueOf(date));
  }

}
