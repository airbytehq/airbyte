/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import io.airbyte.commons.lang.Exceptions;
import java.io.IOException;
import java.sql.SQLException;
import java.util.function.Function;
import lombok.val;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Database object for interacting with a Jooq connection.
 */
public class Database {

  private static final Logger LOGGER = LoggerFactory.getLogger(Database.class);

  private static final long DEFAULT_WAIT_MS = 5 * 1000;

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

  public static Database createWithRetry(final DSLContext dslContext,
                                         final Function<Database, Boolean> isDbReady) {
    Database database = null;
    while (database == null) {
      try {
        val infinity = Integer.MAX_VALUE;
        database = createWithRetryTimeout(dslContext, isDbReady, infinity);
      } catch (final IOException e) {
        // This should theoretically never happen since we set the timeout to be a very high number.
      }
    }

    LOGGER.info("Database available!");
    return database;
  }

  public static Database createWithRetryTimeout(final DSLContext dslContext,
                                                final Function<Database, Boolean> isDbReady,
                                                final long timeoutMs)
      throws IOException {
    Database database = null;
    var totalTime = 0;
    while (database == null) {
      LOGGER.warn("Waiting for database to become available...");
      if (totalTime >= timeoutMs) {
        throw new IOException("Unable to connect to database.");
      }

      try {
        database = new Database(dslContext);
        if (!isDbReady.apply(database)) {
          LOGGER.info("Database is not ready yet. Please wait a moment, it might still be initializing...");
          database = null;
          Exceptions.toRuntime(() -> Thread.sleep(DEFAULT_WAIT_MS));
          totalTime += DEFAULT_WAIT_MS;
        }
      } catch (final Exception e) {
        // Ignore the exception because this likely means that the database server is still initializing.
        LOGGER.warn("Ignoring exception while trying to request database:", e);
        database = null;
        Exceptions.toRuntime(() -> Thread.sleep(DEFAULT_WAIT_MS));
        totalTime += DEFAULT_WAIT_MS;
      }
    }
    return database;
  }

}
