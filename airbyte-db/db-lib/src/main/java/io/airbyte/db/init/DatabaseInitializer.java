/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.init;

import static org.jooq.impl.DSL.select;

import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.check.DatabaseAvailabilityCheck;
import io.airbyte.db.check.DatabaseCheckException;
import java.io.IOException;
import java.util.Collection;
import java.util.Optional;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;

/**
 * Performs the initialization of the configured database if the database is available and has not
 * yet been initialized.
 *
 * In the future, this logic could be completely removed if the schema initialization script is
 * converted to a migration script.
 */
public interface DatabaseInitializer {

  /**
   * Initializes the configured database by using the following steps:
   *
   * <ol>
   * <li>Verify that the database is available and accepting connections</li>
   * <li>Verify that the database is populated with the initial schema. If not, create the initial
   * schema.</li>
   * </ol>
   *
   * @throws DatabaseInitializationException if unable to verify the database availability.
   */
  default void initialize() throws DatabaseInitializationException {
    // Verify that the database is up and reachable first
    final Optional<DatabaseAvailabilityCheck> availabilityCheck = getDatabaseAvailabilityCheck();
    if (availabilityCheck.isPresent()) {
      try {
        availabilityCheck.get().check();
        final Optional<DSLContext> dslContext = getDslContext();
        if (dslContext.isPresent()) {
          final Database database = new Database(dslContext.get());
          new ExceptionWrappingDatabase(database).transaction(this::initializeSchema);
        } else {
          throw new DatabaseInitializationException("Database configuration not present.");
        }
      } catch (final DatabaseCheckException | IOException e) {
        throw new DatabaseInitializationException("Database availability check failed.", e);
      }
    } else {
      throw new DatabaseInitializationException("Availability check not configured.");
    }
  }

  /**
   * Tests whether the provided table exists in the database.
   *
   * @param ctx A {@link DSLContext} used to query the database.
   * @param tableName The name of the table.
   * @return {@code True} if the table exists or {@code false} otherwise.
   */
  default boolean hasTable(final DSLContext ctx, final String tableName) {
    return ctx.fetchExists(select()
        .from("information_schema.tables")
        .where(DSL.field("table_name").eq(tableName)
            .and(DSL.field("table_schema").eq("public"))));
  }

  /**
   * Initializes the schema in the database represented by the provided {@link DSLContext} instance.
   *
   * If the initial tables already exist in the database, initialization is skipped. Otherwise, the
   * script provided by the {@link #getInitialSchema()} method is executed against the database.
   *
   * @param ctx The {@link DSLContext} used to execute the schema initialization.
   * @return {@code true} indicating that the operation ran
   */
  default boolean initializeSchema(final DSLContext ctx) {
    final Optional<Collection<String>> tableNames = getTableNames();

    if (tableNames.isPresent()) {
      // Verify that all the required tables are present
      if (tableNames.get().stream().allMatch(tableName -> hasTable(ctx, tableName))) {
        getLogger().info("The {} database is initialized", getDatabaseName());
      } else {
        getLogger().info("The {} database has not been initialized; initializing it with schema: \n{}", getDatabaseName(),
            getInitialSchema());
        ctx.execute(getInitialSchema());
        getLogger().info("The {} database successfully initialized with schema: \n{}.", getDatabaseName(), getInitialSchema());
      }
      return true;
    } else {
      getLogger().warn("Initial collection of table names is empty.  Cannot perform schema check.");
      return false;
    }
  }

  /**
   * Retrieves the {@link DatabaseAvailabilityCheck} used to verify that the database is running and
   * available.
   *
   * @return The {@link DatabaseAvailabilityCheck}.
   */
  Optional<DatabaseAvailabilityCheck> getDatabaseAvailabilityCheck();

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
   * Retrieve the initial schema to be applied to the database if the database is not already
   * populated with the expected table(s).
   *
   * @return The initial schema.
   */
  String getInitialSchema();

  /**
   * Retrieves the configured {@link Logger} object to be used to record progress of the migration
   * check.
   *
   * @return The configured {@link Logger} object.
   */
  Logger getLogger();

  /**
   * The collection of table names that will be used to confirm database availability.
   *
   * @return The collection of database table names.
   */
  Optional<Collection<String>> getTableNames();

}
