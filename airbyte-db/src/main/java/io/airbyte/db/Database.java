package io.airbyte.db;

import java.sql.Connection;
import java.sql.SQLException;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Database implements AutoCloseable {

  private final static Logger LOGGER = LoggerFactory.getLogger(Database.class);

  private final BasicDataSource bds;
  private final SQLDialect dialect;

  public Database(final BasicDataSource bds, final SQLDialect dialect) {
    this.bds = bds;
    this.dialect = dialect;
  }

  public Connection getConnection() throws SQLException {
    return bds.getConnection();
  }

  public <T> T query(ContextQueryFunction<T> transform) throws SQLException {
    return transform.apply(DSL.using(bds, dialect));
  }

  public <T> T transaction(ContextQueryFunction<T> transform) throws SQLException {
    return DSL.using(bds, dialect).transactionResult(configuration -> transform.apply(DSL.using(configuration)));
  }

  @Override
  public void close() throws Exception {
    bds.close();
  }
}
