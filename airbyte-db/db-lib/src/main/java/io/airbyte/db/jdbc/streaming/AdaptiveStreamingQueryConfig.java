/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AdaptiveStreamingQueryConfig implements JdbcStreamingQueryConfig {

  private static final Logger LOGGER = LoggerFactory.getLogger(AdaptiveStreamingQueryConfig.class);
  // log fetch size change after there are LOG_ENTRY_SIZE
  // adjustments to prevent excessive logging
  private static final int LOG_ENTRY_SIZE = 10;

  private final List<Integer> fetchSizeChanges = new ArrayList<>(LOG_ENTRY_SIZE);
  private final FetchSizeEstimator fetchSizeEstimator;
  private int currentFetchSize;

  public AdaptiveStreamingQueryConfig() {
    this.fetchSizeEstimator = TwoStageSizeEstimator.getInstance();
    this.currentFetchSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE;
  }

  @Override
  public void initialize(final Connection connection, final Statement preparedStatement) throws SQLException {
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(FetchSizeConstants.INITIAL_SAMPLE_SIZE);
    currentFetchSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE;
    LOGGER.info("Set initial fetch size: {} rows", preparedStatement.getFetchSize());
  }

  @Override
  public void accept(final ResultSet resultSet, final Object rowData) throws SQLException {
    fetchSizeEstimator.accept(rowData);
    final Optional<Integer> newFetchSize = fetchSizeEstimator.getFetchSize();

    if (newFetchSize.isPresent() && currentFetchSize != newFetchSize.get()) {
      currentFetchSize = newFetchSize.get();
      resultSet.setFetchSize(currentFetchSize);

      if (fetchSizeChanges.size() < LOG_ENTRY_SIZE) {
        fetchSizeChanges.add(currentFetchSize);
      } else {
        LOGGER.info("Last {} fetch size updates: {}", LOG_ENTRY_SIZE, fetchSizeChanges);
        fetchSizeChanges.clear();
      }
    }
  }

}
