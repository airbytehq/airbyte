/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.io.IOException;
import java.sql.SQLException;

/**
 * Wraps a {@link Database} object and throwing IOExceptions instead of SQLExceptions.
 */
public class ExceptionWrappingDatabase implements AutoCloseable {

  private final Database database;

  public ExceptionWrappingDatabase(Database database) {
    this.database = database;
  }

  public <T> T query(ContextQueryFunction<T> transform) throws IOException {
    try {
      return database.query(transform);
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  public <T> T transaction(ContextQueryFunction<T> transform) throws IOException {
    try {
      return database.transaction(transform);
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public void close() throws Exception {
    database.close();
  }

}
