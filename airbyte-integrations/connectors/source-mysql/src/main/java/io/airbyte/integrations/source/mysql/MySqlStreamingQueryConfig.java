/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlStreamingQueryConfig extends AdaptiveStreamingQueryConfig {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlStreamingQueryConfig.class);

  public MySqlStreamingQueryConfig() {
    super();
  }

  @Override
  public void initialize(final Connection connection, final Statement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(Integer.MIN_VALUE);
    LOGGER.info("Set initial fetch size: {} rows", preparedStatement.getFetchSize());
  }

}
