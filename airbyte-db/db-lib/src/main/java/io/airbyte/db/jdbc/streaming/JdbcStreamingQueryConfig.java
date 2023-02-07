/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import io.airbyte.commons.functional.CheckedBiConsumer;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/*
 * Interface that defines how to stream results from a Jdbc database. This involves determining
 * updating what the fetch size should be based on the size of the existing rows. 1. The config
 * initializes the fetch size and sets up the estimator. 2. The config then accepts each row and
 * feeds it to the estimator. If the estimator has a new estimate, it updates the fetch size.
 */

public interface JdbcStreamingQueryConfig extends CheckedBiConsumer<ResultSet, Object, SQLException> {

  void initialize(final Connection connection, final Statement statement) throws SQLException;

}
