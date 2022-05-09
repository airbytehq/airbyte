/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.util.Map;
import javax.sql.DataSource;

/**
 * Temporary factory class that provides convenience methods for creating a {@link DataSource}
 * instance. This class will be removed once the project has been converted to leverage an
 * application framework to manage the creation and injection of {@link DataSource} objects.
 *
 * This class replaces direct calls to {@link io.airbyte.db.Databases}.
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
   * Builder class used to configure and construct {@link DataSource} instances.
   */
  private static class DataSourceBuilder {

    private static final Map<String, String> JDBC_URL_FORMATS = Map.of("org.postgresql.Driver", "jdbc:postgresql://%s:%d/%s",
        "com.amazon.redshift.jdbc.Driver", "jdbc:redshift://%s:%d/%s",
        "com.mysql.cj.jdbc.Driver", "jdbc:mysql://%s:%d/%s",
        "com.microsoft.sqlserver.jdbc.SQLServerDriver", "jdbc:sqlserver://%s:%d/%s",
        "oracle.jdbc.OracleDriver", "jdbc:oracle:thin:@%s:%d:%s",
        "ru.yandex.clickhouse.ClickHouseDriver", "jdbc:ch://%s:%d/%s",
        "org.mariadb.jdbc.Driver", "jdbc:mariadb://%s:%d/%s");

    private Map<String, String> connectionProperties = Map.of();
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

      connectionProperties.forEach(config::addDataSourceProperty);

      final HikariDataSource dataSource = new HikariDataSource(config);
      dataSource.validate();
      return dataSource;
    }

  }

}
