/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.io.Closeable;
import java.sql.SQLException;
import javax.sql.DataSource;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;

/**
 * Database object for interacting with a Jooq connection.
 */
public class Database implements AutoCloseable {

  private final DataSource ds;
  private final SQLDialect dialect;

  public Database(final DataSource ds, final SQLDialect dialect) {
    this.ds = ds;
    this.dialect = dialect;
  }

  public <T> T query(ContextQueryFunction<T> transform) throws SQLException {
    return transform.query(DSL.using(ds, dialect));
  }

  public <T> T transaction(ContextQueryFunction<T> transform) throws SQLException {
    return DSL.using(ds, dialect).transactionResult(configuration -> transform.query(DSL.using(configuration)));
  }

  public DataSource getDataSource() {
    return ds;
  }

  @Override
  public void close() throws Exception {
    // Just a safety in case we are using a datasource implementation that requires closing.
    // BasicDataSource from apache does since it also provides a pooling mechanism to reuse connections.

    if (ds instanceof AutoCloseable) {
      ((AutoCloseable) ds).close();
    }
    if (ds instanceof Closeable) {
      ((Closeable) ds).close();
    }
  }

}
