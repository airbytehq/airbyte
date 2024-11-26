/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.pervasive;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.airbyte.cdk.db.jdbc.streaming.JdbcStreamingQueryConfig;
import io.airbyte.cdk.db.jdbc.streaming.FetchSizeEstimator;
import io.airbyte.cdk.db.jdbc.streaming.TwoStageSizeEstimator;

public class PervasiveAdaptiveStreamingQueryConfig implements JdbcStreamingQueryConfig {

  private static final Logger LOGGER = LoggerFactory.getLogger(PervasiveAdaptiveStreamingQueryConfig.class);
  private final FetchSizeEstimator fetchSizeEstimator;
  private int currentFetchSize;

  public PervasiveAdaptiveStreamingQueryConfig() {
    this.fetchSizeEstimator = TwoStageSizeEstimator.getInstance();
    this.currentFetchSize = 20000;
  }

  @Override
  public void initialize(final Connection connection, final Statement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(this.currentFetchSize);
    LOGGER.info("Set initial fetch size: {} rows", preparedStatement.getFetchSize());
  }

  @Override
  public void accept(final ResultSet resultSet, final Object rowData) throws SQLException {
    fetchSizeEstimator.accept(rowData);
    final Optional<Integer> newFetchSize = fetchSizeEstimator.getFetchSize();

    // this is an issue for pervasive !
    if (newFetchSize.isPresent() && currentFetchSize != newFetchSize.get()) {
      LOGGER.info("Set new fetch size: {} rows", newFetchSize.get());
      // resultSet.setFetchSize(20000);
      // currentFetchSize = newFetchSize.get();
    }
  }

}
