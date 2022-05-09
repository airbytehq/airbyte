/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import static org.jooq.impl.DSL.select;

import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.util.Set;
import java.util.function.Function;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseDatabaseInstance implements DatabaseInstance {

  // Public so classes consuming the getInitialized method have a sense of the time taken.
  public static final long DEFAULT_CONNECTION_TIMEOUT_MS = 30 * 1000;

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseDatabaseInstance.class);

  protected final DSLContext dslContext;
  protected final String databaseName;
  protected final Set<String> initialExpectedTables;
  protected final String initialSchema;
  protected final Function<Database, Boolean> isDatabaseReady;

  /**
   * @param dslContext The configured {@link DSLContext}.
   * @param databaseName this name is only for logging purpose; it may not be the actual database name
   *        in the server
   * @param initialSchema the initial database structure.
   * @param initialExpectedTables The set of tables that should be present in order to consider the
   *        database ready for use.
   * @param isDatabaseReady a function to check if the database has been initialized and ready for
   *        consumption
   */
  protected BaseDatabaseInstance(final DSLContext dslContext,
                                 final String databaseName,
                                 final String initialSchema,
                                 final Set<String> initialExpectedTables,
                                 final Function<Database, Boolean> isDatabaseReady) {
    this.dslContext = dslContext;
    this.databaseName = databaseName;
    this.initialSchema = initialSchema;
    this.initialExpectedTables = initialExpectedTables;
    this.isDatabaseReady = isDatabaseReady;
  }

  @Override
  public boolean isInitialized() throws IOException {
    final Database database = Database.createWithRetryTimeout(dslContext,
        isDatabaseConnected(databaseName),
        DEFAULT_CONNECTION_TIMEOUT_MS);
    return new ExceptionWrappingDatabase(database).transaction(ctx -> initialExpectedTables.stream().allMatch(tableName -> hasTable(ctx, tableName)));
  }

  @Override
  public Database getInitialized() {
    // When we don't need to setup the database, it means the database is initialized
    // somewhere else, and it is considered ready only when data has been loaded into it.
    return Database.createWithRetry(dslContext, isDatabaseReady);
  }

  @Override
  public Database getAndInitialize() throws IOException {
    // When we need to setup the database, it means the database will be initialized after
    // we connect to the database. So the database itself is considered ready as long as
    // the connection is alive.
    final Database database = Database.createWithRetry(dslContext, isDatabaseConnected(databaseName));

    new ExceptionWrappingDatabase(database).transaction(ctx -> {
      final boolean hasTables = initialExpectedTables.stream().allMatch(tableName -> hasTable(ctx, tableName));
      if (hasTables) {
        LOGGER.info("The {} database has been initialized", databaseName);
        return null;
      }
      LOGGER.info("The {} database has not been initialized; initializing it with schema: {}", databaseName, initialSchema);
      ctx.execute(initialSchema);
      return null;
    });

    return database;
  }

  /**
   * @return true if the table exists.
   */
  protected static boolean hasTable(final DSLContext ctx, final String tableName) {
    return ctx.fetchExists(select()
        .from("information_schema.tables")
        .where(DSL.field("table_name").eq(tableName)
            .and(DSL.field("table_schema").eq("public"))));
  }

  /**
   * @return true if the table has data.
   */
  protected static boolean hasData(final DSLContext ctx, final String tableName) {
    return ctx.fetchExists(select().from(tableName));
  }

  protected static Function<Database, Boolean> isDatabaseConnected(final String databaseName) {
    return database -> {
      try {
        LOGGER.info("Testing {} database connection...", databaseName);
        return database.query(ctx -> ctx.fetchExists(select().from("information_schema.tables")));
      } catch (final Exception e) {
        return false;
      }
    };
  }

}
