/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.io.IOException;
import java.sql.SQLException;

/**
 * Wraps a {@link Database} object and throwing IOExceptions instead of SQLExceptions.
 */
public class ExceptionWrappingDatabase {

  private final Database database;

  public ExceptionWrappingDatabase(final Database database) {
    this.database = database;
  }

  public <T> T query(final ContextQueryFunction<T> transform) throws IOException {
    try {
      return database.query(transform);
    } catch (final SQLException e) {
      throw new IOException(e);
    }
  }

  public <T> T transaction(final ContextQueryFunction<T> transform) throws IOException {
    try {
      return database.transaction(transform);
    } catch (final SQLException e) {
      throw new IOException(e);
    }
  }

}
