/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.bigquery;

import io.airbyte.db.ContextQueryFunction;
import io.airbyte.db.Database;
import java.sql.SQLException;
import javax.annotation.Nullable;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.SQLDialect;
import org.jooq.exception.DataAccessException;
import org.jooq.impl.DefaultDSLContext;

/**
 * This class is a temporary and will be removed as part of the issue @TODO #4547
 */
public class TempBigQueryJoolDatabaseImpl extends Database {

  private final BigQueryDatabase realDatabase;

  public TempBigQueryJoolDatabaseImpl(final String projectId, final String jsonCreds) {
    super(null);
    realDatabase = createBigQueryDatabase(projectId, jsonCreds);
  }

  @Override
  public <T> T query(final ContextQueryFunction<T> transform) throws SQLException {
    return transform.query(new FakeDefaultDSLContext(realDatabase));
  }

  @Override
  public <T> T transaction(final ContextQueryFunction<T> transform) throws SQLException {
    return transform.query(new FakeDefaultDSLContext(realDatabase));
  }

  public BigQueryDatabase getRealDatabase() {
    return realDatabase;
  }

  private static class FakeDefaultDSLContext extends DefaultDSLContext {

    private final BigQueryDatabase database;

    public FakeDefaultDSLContext(final BigQueryDatabase database) {
      super((SQLDialect) null);
      this.database = database;
    }

    @Override
    @Nullable
    public Result<Record> fetch(final String sql) throws DataAccessException {
      try {
        database.execute(sql);
      } catch (final SQLException e) {
        throw new DataAccessException(e.getMessage());
      }
      return null;
    }

  }

  public static BigQueryDatabase createBigQueryDatabase(final String projectId, final String jsonCreds) {
    return new BigQueryDatabase(projectId, jsonCreds);
  }

}
