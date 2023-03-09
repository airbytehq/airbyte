/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.DateTimeConverter;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.ResultSet;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSourceOperations.class);

  /**
   * Oracle's DATE type can actually have time values, so we return a full timestamp.
   */
  @Override
  protected void putDate(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    node.put(columnName, DateTimeConverter.convertToTimestamp(resultSet.getTimestamp(index)));
  }

}
