/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalUnit;
import java.util.Map;
import java.util.Optional;

public abstract class JdbcConnector extends BaseConnector {

  public static final String POSTGRES_CONNECT_TIMEOUT_KEY = "connectTimeout";
  public static final Duration POSTGRES_CONNECT_TIMEOUT_DEFAULT_DURATION = Duration.ofSeconds(10);

  public static final String CONNECT_TIMEOUT_KEY = "connectTimeout";
  public static final Duration CONNECT_TIMEOUT_DEFAULT = Duration.ofSeconds(60);

  protected final String driverClassName;

  protected JdbcConnector(String driverClassName) {
    this.driverClassName = driverClassName;
  }

  protected Duration getConnectionTimeout(final Map<String, String> connectionProperties) {
    return getConnectionTimeout(connectionProperties, driverClassName);
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
      case POSTGRESQL -> maybeParseDuration(connectionProperties.get(POSTGRES_CONNECT_TIMEOUT_KEY), ChronoUnit.SECONDS)
          .or(() -> Optional.of(POSTGRES_CONNECT_TIMEOUT_DEFAULT_DURATION));
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

}
