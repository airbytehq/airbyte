/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

/**
 * Collection of JDBC driver class names and the associated JDBC URL format string.
 */
public enum DatabaseDriver {

  POSTGRESQL("org.postgresql.Driver", "jdbc:postgresql://%s:%d/%s");

  private final String driverClassName;
  private final String urlFormatString;

  DatabaseDriver(final String driverClassName, final String urlFormatString) {
    this.driverClassName = driverClassName;
    this.urlFormatString = urlFormatString;
  }

  public String getDriverClassName() {
    return driverClassName;
  }

  public String getUrlFormatString() {
    return urlFormatString;
  }

  /**
   * Finds the {@link DatabaseDriver} enumerated value that matches the provided driver class name.
   *
   * @param driverClassName The driver class name.
   * @return The matching {@link DatabaseDriver} enumerated value or {@code null} if no match is
   *         found.
   */
  public static DatabaseDriver findByDriverClassName(final String driverClassName) {
    DatabaseDriver selected = null;

    for (final DatabaseDriver candidate : values()) {
      if (candidate.getDriverClassName().equalsIgnoreCase(driverClassName)) {
        selected = candidate;
        break;
      }
    }

    return selected;
  }

}
