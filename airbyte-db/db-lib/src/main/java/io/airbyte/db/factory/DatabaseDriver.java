/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

/**
 * Collection of JDBC driver class names and the associated JDBC URL format string.
 */
public enum DatabaseDriver {

  CLICKHOUSE("com.clickhouse.jdbc.ClickHouseDriver", "jdbc:clickhouse:%s://%s:%d/%s"),
  DATABRICKS("com.databricks.client.jdbc.Driver", "jdbc:databricks://%s:%s;HttpPath=%s;SSL=1;UserAgentEntry=Airbyte"),
  DB2("com.ibm.db2.jcc.DB2Driver", "jdbc:db2://%s:%d/%s"),
  STARBURST("io.trino.jdbc.TrinoDriver", "jdbc:trino://%s:%s/%s?SSL=true&source=airbyte"),
  MARIADB("org.mariadb.jdbc.Driver", "jdbc:mariadb://%s:%d/%s"),
  MSSQLSERVER("com.microsoft.sqlserver.jdbc.SQLServerDriver", "jdbc:sqlserver://%s:%d/%s"),
  MYSQL("com.mysql.cj.jdbc.Driver", "jdbc:mysql://%s:%d/%s"),
  ORACLE("oracle.jdbc.OracleDriver", "jdbc:oracle:thin:@%s:%d/%s"),
  POSTGRESQL("org.postgresql.Driver", "jdbc:postgresql://%s:%d/%s"),
  REDSHIFT("com.amazon.redshift.jdbc.Driver", "jdbc:redshift://%s:%d/%s"),
  SNOWFLAKE("net.snowflake.client.jdbc.SnowflakeDriver", "jdbc:snowflake://%s/"),
  YUGABYTEDB("com.yugabyte.Driver", "jdbc:yugabytedb://%s:%d/%s"),
  EXASOL("com.exasol.jdbc.EXADriver", "jdbc:exa:%s:%d"),
  TERADATA("com.teradata.jdbc.TeraDriver", "jdbc:teradata://%s/");

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
