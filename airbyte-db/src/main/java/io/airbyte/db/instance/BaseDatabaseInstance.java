/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db.instance;

import static org.jooq.impl.DSL.select;

import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.util.Set;
import java.util.function.Function;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
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
   * @param databaseName this name is only for logging purpose; it may not be the actual database name
   *        in the server
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
        .where(DSL.field("table_name").eq(tableName)
            .and(DSL.field("table_schema").eq("public"))));
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
