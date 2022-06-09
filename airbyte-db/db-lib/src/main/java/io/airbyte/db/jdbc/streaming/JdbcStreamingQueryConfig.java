/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import io.airbyte.commons.functional.CheckedBiConsumer;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public interface JdbcStreamingQueryConfig extends CheckedBiConsumer<ResultSet, Object, SQLException> {

  void initialize(final Connection connection, final Statement statement) throws SQLException;

}
