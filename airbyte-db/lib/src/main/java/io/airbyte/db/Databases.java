/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.bigquery.BigQueryDatabase;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.db.mongodb.MongoDatabase;
import java.io.IOException;
import java.util.Optional;
import java.util.function.Function;
import lombok.val;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Databases {

  private static final Logger LOGGER = LoggerFactory.getLogger(Databases.class);
  private static final long DEFAULT_WAIT_MS = 5 * 1000;

  public static Database createPostgresDatabase(final String username, final String password, final String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "org.postgresql.Driver", SQLDialect.POSTGRES);
  }

  public static Database createPostgresDatabaseWithRetry(final String username,
                                                         final String password,
                                                         final String jdbcConnectionString,
                                                         final Function<Database, Boolean> isDbReady) {
    Database database = null;
    while (database == null) {
      try {
        val infinity = Integer.MAX_VALUE;
        database = createPostgresDatabaseWithRetryTimeout(username, password, jdbcConnectionString, isDbReady, infinity);
      } catch (IOException e) {
        // This should theoretically never happen since we set the timeout to be a very high number.
      }
    }

    LOGGER.info("Database available!");
    return database;
  }

  public static Database createPostgresDatabaseWithRetryTimeout(final String username,
                                                                final String password,
                                                                final String jdbcConnectionString,
                                                                final Function<Database, Boolean> isDbReady,
                                                                final long timeoutMs)
      throws IOException {
    Database database = null;
    if (jdbcConnectionString == null || jdbcConnectionString.trim().equals("")) {
      throw new IllegalArgumentException("Using a null or empty jdbc url will hang database creation; aborting.");
    }

    var totalTime = 0;
    while (database == null) {
      LOGGER.warn("Waiting for database to become available...");
      if (totalTime >= timeoutMs) {
        final var error = String.format("Unable to connection to database at %s..", jdbcConnectionString);
        throw new IOException(error);
      }

      try {
        database = createPostgresDatabase(username, password, jdbcConnectionString);
        if (!isDbReady.apply(database)) {
          LOGGER.info("Database is not ready yet. Please wait a moment, it might still be initializing...");
          database.close();

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

    LOGGER.info("Database available!");
    return database;
  }

  public static JdbcDatabase createRedshiftDatabase(final String username, final String password, final String jdbcConnectionString) {
    return createJdbcDatabase(username, password, jdbcConnectionString, "com.amazon.redshift.jdbc.Driver");
  }

  public static Database createMySqlDatabase(final String username, final String password, final String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "com.mysql.cj.jdbc.Driver", SQLDialect.MYSQL);
  }

  public static Database createSqlServerDatabase(final String username, final String password, final String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "com.microsoft.sqlserver.jdbc.SQLServerDriver", SQLDialect.DEFAULT);
  }

  public static Database createOracleDatabase(final String username, final String password, final String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "oracle.jdbc.OracleDriver", SQLDialect.DEFAULT);
  }

  public static Database createClickhouseDatabase(final String username, final String password, final String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "ru.yandex.clickhouse.ClickHouseDriver", SQLDialect.DEFAULT);
  }

  public static Database createMariaDbDatabase(final String username, final String password, final String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "org.mariadb.jdbc.Driver", SQLDialect.MARIADB);
  }

  public static Database createDatabase(final String username,
                                        final String password,
                                        final String jdbcConnectionString,
                                        final String driverClassName,
                                        final SQLDialect dialect) {
    final BasicDataSource connectionPool = createBasicDataSource(username, password, jdbcConnectionString, driverClassName);

    return new Database(connectionPool, dialect);
  }

  public static Database createDatabase(final String username,
                                        final String password,
                                        final String jdbcConnectionString,
                                        final String driverClassName,
                                        final SQLDialect dialect,
                                        final String connectionProperties) {
    final BasicDataSource connectionPool =
        createBasicDataSource(username, password, jdbcConnectionString, driverClassName, Optional.ofNullable(connectionProperties));

    return new Database(connectionPool, dialect);
  }

  public static JdbcDatabase createJdbcDatabase(final String username,
                                                final String password,
                                                final String jdbcConnectionString,
                                                final String driverClassName) {
    return createJdbcDatabase(username, password, jdbcConnectionString, driverClassName, JdbcUtils.getDefaultSourceOperations());
  }

  public static JdbcDatabase createJdbcDatabase(final String username,
                                                final String password,
                                                final String jdbcConnectionString,
                                                final String driverClassName,
                                                final JdbcSourceOperations sourceOperations) {
    final BasicDataSource connectionPool = createBasicDataSource(username, password, jdbcConnectionString, driverClassName);

    return new DefaultJdbcDatabase(connectionPool, sourceOperations);
  }

  public static JdbcDatabase createJdbcDatabase(final String username,
                                                final String password,
                                                final String jdbcConnectionString,
                                                final String driverClassName,
                                                final String connectionProperties) {
    return createJdbcDatabase(username, password, jdbcConnectionString, driverClassName, connectionProperties,
        JdbcUtils.getDefaultSourceOperations());
  }

  public static JdbcDatabase createJdbcDatabase(final String username,
                                                final String password,
                                                final String jdbcConnectionString,
                                                final String driverClassName,
                                                final String connectionProperties,
                                                final JdbcCompatibleSourceOperations<?> sourceOperations) {
    final BasicDataSource connectionPool =
        createBasicDataSource(username, password, jdbcConnectionString, driverClassName, Optional.ofNullable(connectionProperties));

    return new DefaultJdbcDatabase(connectionPool, sourceOperations);
  }

  public static JdbcDatabase createStreamingJdbcDatabase(final String username,
                                                         final String password,
                                                         final String jdbcConnectionString,
                                                         final String driverClassName,
                                                         final JdbcStreamingQueryConfiguration jdbcStreamingQuery,
                                                         final String connectionProperties,
                                                         final JdbcCompatibleSourceOperations<?> sourceOperations) {
    final BasicDataSource connectionPool =
        createBasicDataSource(username, password, jdbcConnectionString, driverClassName, Optional.ofNullable(connectionProperties));

    final JdbcDatabase defaultJdbcDatabase =
        createJdbcDatabase(username, password, jdbcConnectionString, driverClassName, connectionProperties, sourceOperations);
    return new StreamingJdbcDatabase(connectionPool, defaultJdbcDatabase, jdbcStreamingQuery);
  }

  private static BasicDataSource createBasicDataSource(final String username,
                                                       final String password,
                                                       final String jdbcConnectionString,
                                                       final String driverClassName) {
    return createBasicDataSource(username, password, jdbcConnectionString, driverClassName,
        Optional.empty());
  }

  private static BasicDataSource createBasicDataSource(final String username,
                                                       final String password,
                                                       final String jdbcConnectionString,
                                                       final String driverClassName,
                                                       final Optional<String> connectionProperties) {
    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName(driverClassName);
    connectionPool.setUsername(username);
    connectionPool.setPassword(password);
    connectionPool.setInitialSize(0);
    connectionPool.setMaxTotal(5);
    connectionPool.setUrl(jdbcConnectionString);
    connectionProperties.ifPresent(connectionPool::setConnectionProperties);
    return connectionPool;
  }

  public static BigQueryDatabase createBigQueryDatabase(final String projectId, final String jsonCreds) {
    return new BigQueryDatabase(projectId, jsonCreds);
  }

  public static MongoDatabase createMongoDatabase(final String connectionString, final String databaseName) {
    return new MongoDatabase(connectionString, databaseName);
  }

}
