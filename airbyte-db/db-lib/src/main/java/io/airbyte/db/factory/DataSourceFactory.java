/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import static org.postgresql.PGProperty.CONNECT_TIMEOUT;

import com.google.common.base.Preconditions;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.io.Closeable;
import java.time.Duration;
import java.util.Map;
import java.util.Objects;
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
    return new DataSourceBuilder()
        .withDriverClassName(driverClassName)
        .withJdbcUrl(jdbcConnectionString)
        .withPassword(password)
        .withUsername(username)
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
                                  final Map<String, String> connectionProperties) {
    return new DataSourceBuilder()
        .withConnectionProperties(connectionProperties)
        .withDriverClassName(driverClassName)
        .withJdbcUrl(jdbcConnectionString)
        .withPassword(password)
        .withUsername(username)
        .withConnectionTimeoutMs(DataSourceBuilder.getConnectionTimeoutMs(connectionProperties, driverClassName))
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
    return new DataSourceBuilder()
        .withDatabase(database)
        .withDriverClassName(driverClassName)
        .withHost(host)
        .withPort(port)
        .withPassword(password)
        .withUsername(username)
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
    return new DataSourceBuilder()
        .withConnectionProperties(connectionProperties)
        .withDatabase(database)
        .withDriverClassName(driverClassName)
        .withHost(host)
        .withPort(port)
        .withPassword(password)
        .withUsername(username)
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
    return new DataSourceBuilder()
        .withDatabase(database)
        .withDriverClassName("org.postgresql.Driver")
        .withHost(host)
        .withPort(port)
        .withPassword(password)
        .withUsername(username)
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
      if (dataSource instanceof AutoCloseable closeable) {
        closeable.close();
      }
    }
  }

  /**
   * Builder class used to configure and construct {@link DataSource} instances.
   */
  private static class DataSourceBuilder {

    private Map<String, String> connectionProperties = Map.of();
    private String database;
    private String driverClassName;
    private String host;
    private String jdbcUrl;
    private int maximumPoolSize = 10;
    private int minimumPoolSize = 0;
    private long connectionTimeoutMs;
    private String password;
    private int port = 5432;
    private String username;
    private static final String CONNECT_TIMEOUT_KEY = "connectTimeout";
    private static final Duration CONNECT_TIMEOUT_DEFAULT = Duration.ofSeconds(60);

    private DataSourceBuilder() {}

    /**
     * Retrieves connectionTimeout value from connection properties in seconds, default minimum timeout
     * is 60 seconds since Hikari default of 30 seconds is not enough for acceptance tests. In the case
     * the value is 0, pass the value along as Hikari and Postgres use default max value for 0 timeout
     * value
     *
     * NOTE: HikariCP uses milliseconds for all time values:
     * https://github.com/brettwooldridge/HikariCP#gear-configuration-knobs-baby whereas Postgres is
     * measured in seconds: https://jdbc.postgresql.org/documentation/head/connect.html
     *
     * @param connectionProperties custom jdbc_url_parameters containing information on connection
     *        properties
     * @param driverClassName name of the JDBC driver
     * @return DataSourceBuilder class used to create dynamic fields for DataSource
     */
    private static long getConnectionTimeoutMs(final Map<String, String> connectionProperties, String driverClassName) {
      // TODO: the usage of CONNECT_TIMEOUT is Postgres specific, may need to extend for other databases
      if (driverClassName.equals(DatabaseDriver.POSTGRESQL.getDriverClassName())) {
        final String pgPropertyConnectTimeout = CONNECT_TIMEOUT.getName();
        // If the PGProperty.CONNECT_TIMEOUT was set by the user, then take its value, if not take the
        // default
        if (connectionProperties.containsKey(pgPropertyConnectTimeout)
            && (Long.parseLong(connectionProperties.get(pgPropertyConnectTimeout)) >= 0)) {
          return Duration.ofSeconds(Long.parseLong(connectionProperties.get(pgPropertyConnectTimeout))).toMillis();
        } else {
          return Duration.ofSeconds(Long.parseLong(Objects.requireNonNull(CONNECT_TIMEOUT.getDefaultValue()))).toMillis();
        }
      }
      final Duration connectionTimeout;
      connectionTimeout =
          connectionProperties.containsKey(CONNECT_TIMEOUT_KEY) ? Duration.ofSeconds(Long.parseLong(connectionProperties.get(CONNECT_TIMEOUT_KEY)))
              : CONNECT_TIMEOUT_DEFAULT;
      if (connectionTimeout.getSeconds() == 0) {
        return connectionTimeout.toMillis();
      } else {
        return (connectionTimeout.compareTo(CONNECT_TIMEOUT_DEFAULT) > 0 ? connectionTimeout : CONNECT_TIMEOUT_DEFAULT).toMillis();
      }
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

    public DataSourceBuilder withConnectionTimeoutMs(final Long connectionTimeoutMs) {
      if (connectionTimeoutMs != null) {
        this.connectionTimeoutMs = connectionTimeoutMs;
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
      final DatabaseDriver databaseDriver = DatabaseDriver.findByDriverClassName(driverClassName);

      Preconditions.checkNotNull(databaseDriver, "Unknown or blank driver class name: '" + driverClassName + "'.");

      final HikariConfig config = new HikariConfig();

      config.setDriverClassName(databaseDriver.getDriverClassName());
      config.setJdbcUrl(jdbcUrl != null ? jdbcUrl : String.format(databaseDriver.getUrlFormatString(), host, port, database));
      config.setMaximumPoolSize(maximumPoolSize);
      config.setMinimumIdle(minimumPoolSize);
      config.setConnectionTimeout(connectionTimeoutMs);
      config.setPassword(password);
      config.setUsername(username);

      /*
       * Disable to prevent failing on startup. Applications may start prior to the database container
       * being available. To avoid failing to create the connection pool, disable the fail check. This
       * will preserve existing behavior that tests for the connection on first use, not on creation.
       */
      config.setInitializationFailTimeout(Integer.MIN_VALUE);

      connectionProperties.forEach(config::addDataSourceProperty);

      return new HikariDataSource(config);
    }

  }

}
