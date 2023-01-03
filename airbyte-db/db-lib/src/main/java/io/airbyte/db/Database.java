/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;

/**
 * Database object for interacting with a Jooq connection.
 */
public class Database {

  private final DSLContext dslContext;

  public Database(final DSLContext dslContext) {
    this.dslContext = dslContext;
  }

  public <T> T query(final ContextQueryFunction<T> transform) throws SQLException {
    return transform.query(dslContext);
  }

  public <T> T transaction(final ContextQueryFunction<T> transform) throws SQLException {
    return dslContext.transactionResult(configuration -> transform.query(DSL.using(configuration)));
  }

}
