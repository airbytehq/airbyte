/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.sql.SQLException;
import java.util.Optional;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;

/**
 * Database object for interacting with a Jooq connection.
 */
public class Database {

  private final DSLContext dslContext;
  private final Optional<DataSource> maybeDataSource;

  public Database(final DSLContext dslContext) {
    this(dslContext, Optional.empty());
  }

  public Database(final DSLContext dslContext, final Optional<DataSource> maybeDataSource) {
    this.dslContext = dslContext;
    this.maybeDataSource = maybeDataSource;
  }

  public <T> T query(final ContextQueryFunction<T> transform) throws SQLException {
    if (maybeDataSource.isEmpty()) {
      return transform.query(dslContext);
    } else {
      return transform.query(DSL.using(maybeDataSource.get(), SQLDialect.POSTGRES));
    }

  }

  public <T> T transaction(final ContextQueryFunction<T> transform) throws SQLException {
    if (maybeDataSource.isEmpty()) {
      return dslContext.transactionResult(configuration -> transform.query(DSL.using(configuration)));
    } else {
      return DSL.using(maybeDataSource.get(), SQLDialect.POSTGRES).transactionResult(configuration -> transform.query(DSL.using(configuration)));
    }
  }

}
