package io.airbyte.db.instance;

import static org.jooq.impl.DSL.select;

import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.util.Set;
import java.util.function.Function;
import org.jooq.DSLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseDatabaseInstance implements DatabaseInstance {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseDatabaseInstance.class);

  protected final String username;
  protected final String password;
  protected final String connectionString;
  protected final String schema;
  protected final String databaseName;
  protected final Set<String> tableNames;
  protected final Function<Database, Boolean> isDatabaseReady;

  /**
   * @param connectionString in the format of
   *        jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT/${DATABASE_DB}
   */
  protected BaseDatabaseInstance(String username,
                                 String password,
                                 String connectionString,
                                 String schema,
                                 String databaseName,
                                 Set<String> tableNames,
                                 Function<Database, Boolean> isDatabaseReady) {
    this.username = username;
    this.password = password;
    this.connectionString = connectionString;
    this.schema = schema;
    this.databaseName = databaseName;
    this.tableNames = tableNames;
    this.isDatabaseReady = isDatabaseReady;
  }

  @Override
  public Database getInitialized() {
    // When we don't need to setup the database, it means the database is initialized
    // somewhere else, and it is considered ready only when data has been loaded into it.
    return Databases.createPostgresDatabaseWithRetry(
        username,
        password,
        connectionString,
        isDatabaseReady);
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
        isDatabaseConnected(databaseName));

    new ExceptionWrappingDatabase(database).transaction(ctx -> {
      boolean hasTables = tableNames.stream().allMatch(tableName -> hasTable(ctx, tableName));
      if (hasTables) {
        LOGGER.info("The {} database has been initialized", databaseName);
        return null;
      }
      LOGGER.info("The {} database has not been initialized; initializing it with schema: {}", databaseName, schema);
      ctx.execute(schema);
      return null;
    });

    return database;
  }

  /**
   * @return true if the table exists.
   */
  protected static boolean hasTable(DSLContext ctx, String tableName) {
    return ctx.fetchExists(select()
        .from("information_schema.tables")
        .where(String.format("table_name = '%s'", tableName)));
  }

  /**
   * @return true if the table has data.
   */
  protected static boolean hasData(DSLContext ctx, String tableName) {
    return ctx.fetchExists(select().from(tableName));
  }

  protected static Function<Database, Boolean> isDatabaseConnected(String databaseName) {
    return database -> {
      try {
        LOGGER.info("Testing {} database connection...", databaseName);
        return database.query(ctx -> ctx.fetchExists(select().from("information_schema.tables")));
      } catch (Exception e) {
        return false;
      }
    };
  }

}
