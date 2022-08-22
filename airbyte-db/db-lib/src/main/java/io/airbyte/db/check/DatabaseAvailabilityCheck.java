/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check;

import static org.jooq.impl.DSL.select;

import io.airbyte.db.Database;
import java.util.Optional;
import java.util.function.Function;
import org.jooq.DSLContext;
import org.slf4j.Logger;

/**
 * Performs a check to verify that the configured database is available.
 */
public interface DatabaseAvailabilityCheck extends DatabaseCheck {

  /**
   * The number of times to check if the database is available. TODO replace with a default value in a
   * value injection annotation
   */
  int NUM_POLL_TIMES = 10;

  /**
   * Checks whether the configured database is available.
   *
   * @throws DatabaseCheckException if unable to perform the check.
   */
  @Override
  default void check() throws DatabaseCheckException {
    var initialized = false;
    var totalTime = 0;
    final var sleepTime = getTimeoutMs() / NUM_POLL_TIMES;

    while (!initialized) {
      getLogger().warn("Waiting for database to become available...");
      if (totalTime >= getTimeoutMs()) {
        throw new DatabaseCheckException("Unable to connect to the database.");
      }

      final Optional<DSLContext> dslContext = getDslContext();

      if (dslContext.isPresent()) {
        final Database database = new Database(dslContext.get());
        initialized = isDatabaseConnected(getDatabaseName()).apply(database);
        if (!initialized) {
          getLogger().info("Database is not ready yet. Please wait a moment, it might still be initializing...");
          try {
            Thread.sleep(sleepTime);
          } catch (final InterruptedException e) {
            throw new DatabaseCheckException("Unable to wait for database to be ready.", e);
          }
          totalTime += sleepTime;
        } else {
          getLogger().info("Database available.");
        }
      } else {
        throw new DatabaseCheckException("Database configuration not present.");
      }
    }
  }

  /**
   * Generates a {@link Function} that is used to test if a connection can be made to the database by
   * verifying that the {@code information_schema.tables} tables has been populated.
   *
   * @param databaseName The name of the database to test.
   * @return A {@link Function} that can be invoked to test if the database is available.
   */
  default Function<Database, Boolean> isDatabaseConnected(final String databaseName) {
    return database -> {
      try {
        getLogger().info("Testing {} database connection...", databaseName);
        return database.query(ctx -> ctx.fetchExists(select().from("information_schema.tables")));
      } catch (final Exception e) {
        getLogger().error("Failed to verify database connection.", e);
        return false;
      }
    };
  }

  /**
   * Retrieves the configured database name to be tested.
   *
   * @return The name of the database to test.
   */
  String getDatabaseName();

  /**
   * Retrieves the configured {@link DSLContext} to be used to test the database availability.
   *
   * @return The configured {@link DSLContext} object.
   */
  Optional<DSLContext> getDslContext();

  /**
   * Retrieves the configured {@link Logger} object to be used to record progress of the migration
   * check.
   *
   * @return The configured {@link Logger} object.
   */
  Logger getLogger();

  /**
   * Retrieves the timeout in milliseconds for the check. Once this timeout is exceeded, the check
   * will fail with an {@link InterruptedException}.
   *
   * @return The timeout in milliseconds for the check.
   */
  long getTimeoutMs();

}
