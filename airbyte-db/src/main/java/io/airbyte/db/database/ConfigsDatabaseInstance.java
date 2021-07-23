package io.airbyte.db.database;

import static org.jooq.impl.DSL.select;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigsDatabaseInstance implements DatabaseInstance {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigsDatabaseInstance.class);
  private static final Function<Database, Boolean> IS_CONFIGS_DATABASE_CONNECTED = database -> {
    try {
      LOGGER.info("Testing configs database connection...");
      return database.query(ctx -> ctx.fetchExists(select().from("information_schema.tables")));
    } catch (Exception e) {
      return false;
    }
  };
  private static final Function<Database, Boolean> IS_CONFIGS_DATABASE_READY = database -> {
    try {
      LOGGER.info("Testing if airbyte_configs has been created...");
      return database.query(ctx -> ctx.fetchExists(select().from("airbyte_configs")));
    } catch (Exception e) {
      return false;
    }
  };

  private final String username;
  private final String password;
  private final String connectionString;
  private final String schema;

  /**
   * @param connectionString in the format of jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT/${DATABASE_DB}
   */
  @VisibleForTesting
  public ConfigsDatabaseInstance(String username, String password, String connectionString, String schema) {
    this.username = username;
    this.password = password;
    this.connectionString = connectionString;
    this.schema = schema;
  }

  public ConfigsDatabaseInstance(String username, String password, String connectionString) throws IOException {
    this.username = username;
    this.password = password;
    this.connectionString = connectionString;
    this.schema = MoreResources.readResource("config_tables/schema.sql");
  }

  @Override
  public Database get() {
    // When we don't need to setup the database, it means the database is initialized
    // somewhere else, and it is considered ready only when data has been loaded into it.
    return Databases.createPostgresDatabaseWithRetry(
        username,
        password,
        connectionString,
        IS_CONFIGS_DATABASE_READY);
  }

  @Override
  public Database getAndInitialize() throws IOException {
    // When we need to setup the database, it means the database will be initialized after
    // we connect to the database. So the database itself is considered ready as long as
    // the connection is alive.
    Database database = Databases.createPostgresDatabaseWithRetry(
        username,
        password,
        connectionString,
        IS_CONFIGS_DATABASE_CONNECTED);

    new ExceptionWrappingDatabase(database).transaction(ctx -> {
      boolean hasConfigsTable = DatabaseInstance.hasTable(ctx, "airbyte_configs");
      if (hasConfigsTable) {
        return null;
      }
      LOGGER.info("Configs database has not been initialized; initializing tables with schema: {}", schema);
      ctx.execute(schema);
      return null;
    });

    return database;
  }

}
