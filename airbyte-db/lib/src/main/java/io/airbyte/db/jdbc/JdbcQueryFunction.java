/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import java.sql.Connection;
import java.sql.SQLException;

@FunctionalInterface
public interface JdbcQueryFunction<T> {

  T query(Connection connection) throws SQLException;

}
