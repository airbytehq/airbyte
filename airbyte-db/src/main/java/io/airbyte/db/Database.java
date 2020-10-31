package io.airbyte.db;

import java.io.Closeable;
import java.sql.Connection;
import java.sql.SQLException;
import javax.sql.DataSource;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Database implements AutoCloseable {

  private final static Logger LOGGER = LoggerFactory.getLogger(Database.class);

  private final DataSource ds;
  private final SQLDialect dialect;

  public Database(final DataSource ds, final SQLDialect dialect) {
    this.ds = ds;
    this.dialect = dialect;
  }

  public Connection getConnection() throws SQLException {
    return ds.getConnection();
  }

  public <T> T query(ContextQueryFunction<T> transform) throws SQLException {
    return transform.apply(DSL.using(ds, dialect));
  }

  public <T> T transaction(ContextQueryFunction<T> transform) throws SQLException {
    return DSL.using(ds, dialect).transactionResult(configuration -> transform.apply(DSL.using(configuration)));
  }

  @Override
  public void close() throws Exception {
    if (ds instanceof AutoCloseable) {
      ((AutoCloseable) ds).close();
    }
    if (ds instanceof Closeable) {
      ((Closeable) ds).close();
    }
  }
}
