/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.bigquery;

import io.airbyte.db.ContextQueryFunction;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import java.sql.SQLException;
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
    super(null, null);
    realDatabase = Databases.createBigQueryDatabase(projectId, jsonCreds);
  }

  @Override
  public <T> T query(ContextQueryFunction<T> transform) throws SQLException {
    return transform.query(new FakeDefaultDSLContext(realDatabase));
  }

  @Override
  public <T> T transaction(ContextQueryFunction<T> transform) throws SQLException {
    return transform.query(new FakeDefaultDSLContext(realDatabase));
  }

  @Override
  public void close() throws Exception {
    realDatabase.close();
  }

  public BigQueryDatabase getRealDatabase() {
    return realDatabase;
  }

  private static class FakeDefaultDSLContext extends DefaultDSLContext {

    private final BigQueryDatabase database;

    public FakeDefaultDSLContext(BigQueryDatabase database) {
      super((SQLDialect) null);
      this.database = database;
    }

    @Override
    public Result<Record> fetch(String sql) throws DataAccessException {
      try {
        database.execute(sql);
      } catch (SQLException e) {
        throw new DataAccessException(e.getMessage());
      }
      return null;
    }

  }

}
