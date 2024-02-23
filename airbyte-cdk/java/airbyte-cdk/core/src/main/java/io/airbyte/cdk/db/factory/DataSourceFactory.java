/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db.factory;

import com.google.common.base.Preconditions;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.io.Closeable;
import java.time.Duration;
import java.util.Map;
import javax.sql.DataSource;

/**
 * Temporary factory class that provides convenience methods for creating a {@link DataSource}
 * instance. This class will be removed once the project has been converted to leverage an
 * application framework to manage the creation and injection of {@link DataSource} objects.
 */
public class DataSourceFactory {

  /**
   * Constructs a new {@link DataSource} using the provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param driverClassName The fully qualified name of the JDBC driver class.
   * @param jdbcConnectionString The JDBC connection string.
   * @return The configured {@link DataSource}.
   */
  public static DataSource create(final String username,
                                  final String password,
                                  final String driverClassName,
                                  final String jdbcConnectionString) {
    return new DataSourceBuilder(username, password, driverClassName, jdbcConnectionString)
        .build();
  }

  /**
   * Constructs a new {@link DataSource} using the provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param driverClassName The fully qualified name of the JDBC driver class.
   * @param jdbcConnectionString The JDBC connection string.
   * @param connectionProperties Additional configuration properties for the underlying driver.
   * @return The configured {@link DataSource}.
   */
  public static DataSource create(final String username,
                                  final String password,
                                  final String driverClassName,
                                  final String jdbcConnectionString,
                                  final Map<String, String> connectionProperties,
                                  final Duration connectionTimeout) {
    return new DataSourceBuilder(username, password, driverClassName, jdbcConnectionString)
        .withConnectionProperties(connectionProperties)
        .withConnectionTimeout(connectionTimeout)
        .build();
  }

  /**
   * Constructs a new {@link DataSource} using the provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param host The host address of the database.
   * @param port The port of the database.
   * @param database The name of the database.
   * @param driverClassName The fully qualified name of the JDBC driver class.
   * @return The configured {@link DataSource}.
   */
  public static DataSource create(final String username,
                                  final String password,
                                  final String host,
                                  final int port,
                                  final String database,
                                  final String driverClassName) {
    return new DataSourceBuilder(username, password, driverClassName, host, port, database)
        .build();
  }

  /**
   * Constructs a new {@link DataSource} using the provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param host The host address of the database.
   * @param port The port of the database.
   * @param database The name of the database.
   * @param driverClassName The fully qualified name of the JDBC driver class.
   * @param connectionProperties Additional configuration properties for the underlying driver.
   * @return The configured {@link DataSource}.
   */
  public static DataSource create(final String username,
                                  final String password,
                                  final String host,
                                  final int port,
                                  final String database,
                                  final String driverClassName,
                                  final Map<String, String> connectionProperties) {
    return new DataSourceBuilder(username, password, driverClassName, host, port, database)
        .withConnectionProperties(connectionProperties)
        .build();
  }

  /**
   * Convenience method that constructs a new {@link DataSource} for a PostgreSQL database using the
   * provided configuration.
   *
   * @param username The username of the database user.
   * @param password The password of the database user.
   * @param host The host address of the database.
   * @param port The port of the database.
   * @param database The name of the database.
   * @return The configured {@link DataSource}.
   */
  public static DataSource createPostgres(final String username,
                                          final String password,
                                          final String host,
                                          final int port,
                                          final String database) {
    return new DataSourceBuilder(username, password, "org.postgresql.Driver", host, port, database)
        .build();
  }

  /**
   * Utility method that attempts to close the provided {@link DataSource} if it implements
   * {@link Closeable}.
   *
   * @param dataSource The {@link DataSource} to close.
   * @throws Exception if unable to close the data source.
   */
  public static void close(final DataSource dataSource) throws Exception {
    if (dataSource != null) {
      if (dataSource instanceof final AutoCloseable closeable) {
        closeable.close();
      }
    }
  }

  /**
   * Builder class used to configure and construct {@link DataSource} instances.
   */
  public static class DataSourceBuilder {

    private Map<String, String> connectionProperties = Map.of();
    private String database;
    private String driverClassName;
    private String host;
    private String jdbcUrl;
    private int maximumPoolSize = 10;
    private int minimumPoolSize = 0;
    private Duration connectionTimeout = Duration.ZERO;
    private String password;
    private int port = 5432;
    private String username;
    private String connectionInitSql;

    private DataSourceBuilder(final String username,
                              final String password,
                              final String driverClassName) {
      this.username = username;
      this.password = password;
      this.driverClassName = driverClassName;
    }

    public DataSourceBuilder(final String username,
                             final String password,
                             final String driverClassName,
                             final String jdbcUrl) {
      this(username, password, driverClassName);
      this.jdbcUrl = jdbcUrl;
    }

    public DataSourceBuilder(final String username,
                             final String password,
                             final String driverClassName,
                             final String host,
                             final int port,
                             final String database) {
      this(username, password, driverClassName);
      this.host = host;
      this.port = port;
      this.database = database;
    }

    public DataSourceBuilder withConnectionProperties(final Map<String, String> connectionProperties) {
      if (connectionProperties != null) {
        this.connectionProperties = connectionProperties;
      }
      return this;
    }

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

    public DataSourceBuilder withConnectionTimeout(final Duration connectionTimeout) {
      if (connectionTimeout != null) {
        this.connectionTimeout = connectionTimeout;
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

    public DataSourceBuilder withConnectionInitSql(final String sql) {
      this.connectionInitSql = sql;
      return this;
    }

    public DataSource build() {
      final DatabaseDriver databaseDriver = DatabaseDriver.findByDriverClassName(driverClassName);

      Preconditions.checkNotNull(databaseDriver, "Unknown or blank driver class name: '" + driverClassName + "'.");

      final HikariConfig config = new HikariConfig();

      config.setDriverClassName(databaseDriver.getDriverClassName());
      config.setJdbcUrl(jdbcUrl != null ? jdbcUrl : String.format(databaseDriver.getUrlFormatString(), host, port, database));
      config.setMaximumPoolSize(maximumPoolSize);
      config.setMinimumIdle(minimumPoolSize);
      // HikariCP uses milliseconds for all time values:
      // https://github.com/brettwooldridge/HikariCP#gear-configuration-knobs-baby
      config.setConnectionTimeout(connectionTimeout.toMillis());
      config.setPassword(password);
      config.setUsername(username);

      /*
       * Disable to prevent failing on startup. Applications may start prior to the database container
       * being available. To avoid failing to create the connection pool, disable the fail check. This
       * will preserve existing behavior that tests for the connection on first use, not on creation.
       */
      config.setInitializationFailTimeout(Integer.MIN_VALUE);

      config.setConnectionInitSql(connectionInitSql);

      connectionProperties.forEach(config::addDataSourceProperty);

      return new HikariDataSource(config);
    }

  }

}
