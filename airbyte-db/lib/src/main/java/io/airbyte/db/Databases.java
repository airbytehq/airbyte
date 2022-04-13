/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
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
import java.util.Map;
import java.util.function.Function;
import javax.sql.DataSource;
import lombok.val;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Databases {

  private static final Logger LOGGER = LoggerFactory.getLogger(Databases.class);
  private static final long DEFAULT_WAIT_MS = 5 * 1000;

  public static Database createDatabaseWithRetry(final DSLContext dslContext, final Function<Database, Boolean> isDbReady) {
    Database database = null;
    while (database == null) {
      try {
        val infinity = Integer.MAX_VALUE;
        database = createDatabaseWithRetryTimeout(dslContext, isDbReady, infinity);
      } catch (final IOException e) {
        // This should theoretically never happen since we set the timeout to be a very high number.
      }
    }

    LOGGER.info("Database available!");
    return database;
  }

  public static Database createDatabaseWithRetryTimeout(final DSLContext dslContext,
                                                        final Function<Database, Boolean> isDbReady,
                                                        final long timeoutMs)
      throws IOException {
    if (dslContext == null) {
      throw new IllegalArgumentException("DSLContext required.");
    }

    final Database database = createDatabase(dslContext);
    boolean isReady = false;
    var totalTime = 0;
    while (!isReady) {
      LOGGER.warn("Waiting for database to become available...");
      if (totalTime >= timeoutMs) {
        final var error = String.format("Unable to connection to database.");
        throw new IOException(error);
      }

      try {
        isReady = isDbReady.apply(database);
        if (!isReady) {
          LOGGER.info("Database is not ready yet. Please wait a moment, it might still be initializing...");
          Exceptions.toRuntime(() -> Thread.sleep(DEFAULT_WAIT_MS));
          totalTime += DEFAULT_WAIT_MS;
        }
      } catch (final Exception e) {
        // Ignore the exception because this likely means that the database server is still initializing.
        LOGGER.warn("Ignoring exception while trying to request database:", e);
        Exceptions.toRuntime(() -> Thread.sleep(DEFAULT_WAIT_MS));
        totalTime += DEFAULT_WAIT_MS;
      }
    }

    LOGGER.info("Database available!");
    return database;
  }

  public static Database createDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  public static JdbcDatabase createJdbcDatabase(final DataSource dataSource) {
    return createJdbcDatabase(dataSource, JdbcUtils.getDefaultSourceOperations());
  }

  public static JdbcDatabase createJdbcDatabase(final DataSource dataSource,
                                                final JdbcSourceOperations sourceOperations) {
    return new DefaultJdbcDatabase(dataSource, sourceOperations);
  }

  public static JdbcDatabase createJdbcDatabase(final DataSource dataSource,
                                                final JdbcCompatibleSourceOperations<?> sourceOperations) {
    return new DefaultJdbcDatabase(dataSource, sourceOperations);
  }

  public static JdbcDatabase createStreamingJdbcDatabase(final DataSource dataSource,
                                                         final JdbcStreamingQueryConfiguration jdbcStreamingQuery,
                                                         final JdbcCompatibleSourceOperations<?> sourceOperations) {
    return new StreamingJdbcDatabase(dataSource, sourceOperations, jdbcStreamingQuery);
  }

  public static BigQueryDatabase createBigQueryDatabase(final String projectId, final String jsonCreds) {
    return new BigQueryDatabase(projectId, jsonCreds);
  }

  public static MongoDatabase createMongoDatabase(final String connectionString, final String databaseName) {
    return new MongoDatabase(connectionString, databaseName);
  }

  public static DSLContext createDslContext(final DataSource dataSource, final SQLDialect dialect) {
    return DSL.using(dataSource, dialect);
  }

  public static DataSourceBuilder dataSourceBuilder() {
    return new DataSourceBuilder();
  };

  public static class DataSourceBuilder {

    private static final Map<String, String> JDBC_URL_FORMATS = Map.of("org.postgresql.Driver", "jdbc:postgresql://%s:%d/%s",
        "com.amazon.redshift.jdbc.Driver", "jdbc:redshift://%s:%d/%s",
        "com.mysql.cj.jdbc.Driver", "jdbc:mysql://%s:%d/%s",
        "com.microsoft.sqlserver.jdbc.SQLServerDriver", "jdbc:sqlserver://%s:%d/%s",
        "oracle.jdbc.OracleDriver", "jdbc:oracle:thin:@%s:%d:%s",
        "ru.yandex.clickhouse.ClickHouseDriver", "jdbc:ch://%s:%d/%s",
        "org.mariadb.jdbc.Driver", "jdbc:mariadb://%s:%d/%s");

    private String database;
    private String driverClassName = "org.postgresql.Driver";
    private String host;
    private String jdbcUrl;
    private Integer maximumPoolSize = 5;
    private Integer minimumPoolSize = 0;
    private String password;
    private Integer port = 5432;
    private String username;

    private DataSourceBuilder() {}

    public DataSourceBuilder withDatabase(final String database) {
      this.database = database;
      return this;
    }

    public DataSourceBuilder withDriverClassName(final String driverClassName) {
      this.driverClassName = driverClassName;
      return this;
    }

    public DataSourceBuilder withHost(final String host) {
      this.host = host;
      return this;
    }

    public DataSourceBuilder withJdbcUrl(final String jdbcUrl) {
      this.jdbcUrl = jdbcUrl;
      return this;
    }

    public DataSourceBuilder withMaximumPoolSize(final Integer maximumPoolSize) {
      if (maximumPoolSize != null) {
        this.maximumPoolSize = maximumPoolSize;
      }
      return this;
    }

    public DataSourceBuilder withMinimumPoolSize(final Integer minimumPoolSize) {
      if (minimumPoolSize != null) {
        this.minimumPoolSize = minimumPoolSize;
      }
      return this;
    }

    public DataSourceBuilder withPassword(final String password) {
      this.password = password;
      return this;
    }

    public DataSourceBuilder withPort(final Integer port) {
      if (port != null) {
        this.port = port;
      }
      return this;
    }

    public DataSourceBuilder withUsername(final String username) {
      this.username = username;
      return this;
    }

    public DataSource build() {
      final HikariConfig config = new HikariConfig();
      config.setDriverClassName(driverClassName);
      config.setJdbcUrl(jdbcUrl != null ? jdbcUrl : String.format(JDBC_URL_FORMATS.getOrDefault(driverClassName, ""), host, port, database));
      config.setMaximumPoolSize(maximumPoolSize);
      config.setMinimumIdle(minimumPoolSize);
      config.setPassword(password);
      config.setUsername(username);

      final HikariDataSource dataSource = new HikariDataSource(config);
      dataSource.validate();
      return dataSource;
    }

  }

}
