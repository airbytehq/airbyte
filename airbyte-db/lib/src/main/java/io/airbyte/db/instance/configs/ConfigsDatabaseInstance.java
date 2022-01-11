/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.BaseDatabaseInstance;
import io.airbyte.db.instance.DatabaseInstance;
import java.io.IOException;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigsDatabaseInstance extends BaseDatabaseInstance implements DatabaseInstance {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigsDatabaseInstance.class);

  private static final String DATABASE_LOGGING_NAME = "airbyte configs";
  private static final String SCHEMA_PATH = "configs_database/schema.sql";
  private static final Function<Database, Boolean> IS_CONFIGS_DATABASE_READY = database -> {
    try {
      LOGGER.info("Testing if airbyte_configs has been created and seeded...");
      if (database.query(ctx -> hasTable(ctx, "airbyte_configs")) && database.query(ctx -> hasData(ctx, "airbyte_configs"))) {
        return true;
      }

      return database.query(ctx -> hasTable(ctx, "state"));
    } catch (Exception e) {
      return false;
    }
  };

  private Database database;

  @VisibleForTesting
  public ConfigsDatabaseInstance(final String username, final String password, final String connectionString, final String schema) {
    super(username, password, connectionString, schema, DATABASE_LOGGING_NAME, ConfigsDatabaseTables.getTableNames(), IS_CONFIGS_DATABASE_READY);
  }

  public ConfigsDatabaseInstance(final String username, final String password, final String connectionString) throws IOException {
    this(username, password, connectionString, MoreResources.readResource(SCHEMA_PATH));
  }

  @Override
  public boolean isInitialized() throws IOException {
    if (database == null) {
      database = Databases.createPostgresDatabaseWithRetry(
          username,
          password,
          connectionString,
          isDatabaseConnected(databaseName));
    }

    return new ExceptionWrappingDatabase(database).transaction(ctx -> {
      // when we start fresh airbyte instance, we start with airbyte_configs configs table and then flyway
      // breaks the table into individual table.
      // state is the last table created by flyway migration.
      // This is why we check if either of the two tables are present or not
      if (hasTable(ctx, "state") || hasTable(ctx, "airbyte_configs")) {
        LOGGER.info("The {} database is initialized", databaseName);
        return true;
      }
      LOGGER.info("The {} database is not initialized; initializing it with schema", databaseName);
      return false;
    });
  }

  @Override
  public Database getAndInitialize() throws IOException {
    // When we need to setup the database, it means the database will be initialized after
    // we connect to the database. So the database itself is considered ready as long as
    // the connection is alive.
    if (database == null) {
      database = Databases.createPostgresDatabaseWithRetry(
          username,
          password,
          connectionString,
          isDatabaseConnected(databaseName));
    }

    new ExceptionWrappingDatabase(database).transaction(ctx -> {
      if (hasTable(ctx, "state") || hasTable(ctx, "airbyte_configs")) {
        LOGGER.info("The {} database has been initialized", databaseName);
        return null;
      }
      LOGGER.info("The {} database has not been initialized; initializing it with schema: {}", databaseName, initialSchema);
      ctx.execute(initialSchema);
      return null;
    });

    return database;
  }

}
