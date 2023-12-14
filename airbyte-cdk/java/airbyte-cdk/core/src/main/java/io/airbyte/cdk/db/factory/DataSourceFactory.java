/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db.factory;

import static org.postgresql.PGProperty.CONNECT_TIMEOUT;

import com.google.common.base.Preconditions;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.io.Closeable;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalUnit;
import java.util.Map;
import java.util.Optional;
import javax.sql.DataSource;

/**
 * Temporary factory class that provides convenience methods for creating a {@link DataSource}
 * instance. This class will be removed once the project has been converted to leverage an
 * application framework to manage the creation and injection of {@link DataSource} objects.
 */
public class DataSourceFactory {

  public static final String CONNECT_TIMEOUT_KEY = "connectTimeout";
  public static final Duration CONNECT_TIMEOUT_DEFAULT = Duration.ofSeconds(60);

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
                                  final Map<String, String> connectionProperties,
                                  final Duration connectionTimeout) {
    return new DataSourceBuilder()
        .withConnectionProperties(connectionProperties)
        .withDriverClassName(driverClassName)
        .withJdbcUrl(jdbcConnectionString)
        .withPassword(password)
        .withUsername(username)
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
   * Retrieves connectionTimeout value from connection properties in millis, default minimum timeout
   * is 60 seconds since Hikari default of 30 seconds is not enough for acceptance tests. In the case
   * the value is 0, pass the value along as Hikari and Postgres use default max value for 0 timeout
   * value.
   *
   * NOTE: Postgres timeout is measured in seconds:
   * https://jdbc.postgresql.org/documentation/head/connect.html
   *
   * @param connectionProperties custom jdbc_url_parameters containing information on connection
   *        properties
   * @param driverClassName name of the JDBC driver
   * @return DataSourceBuilder class used to create dynamic fields for DataSource
   */
  public static Duration getConnectionTimeout(final Map<String, String> connectionProperties, String driverClassName) {
    final Optional<Duration> parsedConnectionTimeout = switch (DatabaseDriver.findByDriverClassName(driverClassName)) {
      case POSTGRESQL -> maybeParseDuration(connectionProperties.get(CONNECT_TIMEOUT.getName()), ChronoUnit.SECONDS)
          .or(() -> maybeParseDuration(CONNECT_TIMEOUT.getDefaultValue(), ChronoUnit.SECONDS));
      case MYSQL -> maybeParseDuration(connectionProperties.get("connectTimeout"), ChronoUnit.MILLIS);
      case MSSQLSERVER -> maybeParseDuration(connectionProperties.get("loginTimeout"), ChronoUnit.SECONDS);
      default -> maybeParseDuration(connectionProperties.get(CONNECT_TIMEOUT_KEY), ChronoUnit.SECONDS)
          // Enforce minimum timeout duration for unspecified data sources.
          .filter(d -> d.compareTo(CONNECT_TIMEOUT_DEFAULT) >= 0);
    };
    return parsedConnectionTimeout.orElse(CONNECT_TIMEOUT_DEFAULT);
  }

  private static Optional<Duration> maybeParseDuration(final String stringValue, TemporalUnit unit) {
    if (stringValue == null) {
      return Optional.empty();
    }
    final long number;
    try {
      number = Long.parseLong(stringValue);
    } catch (NumberFormatException __) {
      return Optional.empty();
    }
    if (number < 0) {
      return Optional.empty();
    }
    return Optional.of(Duration.of(number, unit));
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
    private Duration connectionTimeout = Duration.ZERO;
    private String password;
    private int port = 5432;
    private String username;

    private DataSourceBuilder() {}

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

      connectionProperties.forEach(config::addDataSourceProperty);

      return new HikariDataSource(config);
    }

  }

}
