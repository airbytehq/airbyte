package io.airbyte.db;

import java.sql.Connection;
import java.sql.SQLException;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.ConnectionProvider;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.jooq.impl.DataSourceConnectionProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseHandle implements AutoCloseable {

  private final static Logger LOGGER = LoggerFactory.getLogger(DatabaseHandle.class);

  private final BasicDataSource bds;
  private final SQLDialect dialect;

  private final ConnectionProvider bdsProvider;

  public DatabaseHandle(final BasicDataSource bds, final SQLDialect dialect) {
    this.bds = bds;
    this.dialect = dialect;

    this.bdsProvider = new DataSourceConnectionProvider(bds);
  }

  public Connection getConnection() throws SQLException {
    return bds.getConnection();
  }

  public <T> T query(ContextQueryFunction<T> transform) throws SQLException {
    try (final DSLContext context = getContext()) {
      return transform.apply(context);
    }
  }

  public <T> T transaction(ContextQueryFunction<T> transform) throws SQLException {
    try (final DSLContext context = getContext()) {
      return context.transactionResult(configuration -> {
        DSLContext transactionContext = DSL.using(configuration);
        return transform.apply(transactionContext);
      });
    }
  }

  public DSLContext getContext() throws SQLException {
//    new DataSourceConnectionProvider(bds)
    return DSL.using(bds.getConnection(), dialect);
  }

  @Override
  public void close() throws Exception {
    bds.close();
  }
}
