/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db.factory;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Collection of JDBC driver class names and the associated JDBC URL format string.
 */
public record DatabaseDriver(String driverClassName, String urlFormatString) {
  public static final DatabaseDriver CLICKHOUSE = new DatabaseDriver("com.clickhouse.jdbc.ClickHouseDriver", "jdbc:clickhouse:%s://%s:%d/%s");
  public static final DatabaseDriver DATABRICKS = new DatabaseDriver ("com.databricks.client.jdbc.Driver", "jdbc:databricks://%s:%s;HttpPath=%s;SSL=1;UserAgentEntry=Airbyte");
  public static final DatabaseDriver DB2 = new DatabaseDriver ("com.ibm.db2.jcc.DB2Driver", "jdbc:db2://%s:%d/%s");
  public static final DatabaseDriver STARBURST = new DatabaseDriver ("io.trino.jdbc.TrinoDriver", "jdbc:trino://%s:%s/%s?SSL=true&source=airbyte");
  public static final DatabaseDriver MARIADB = new DatabaseDriver ("org.mariadb.jdbc.Driver", "jdbc:mariadb://%s:%d/%s");
  public static final DatabaseDriver MSSQLSERVER = new DatabaseDriver ("com.microsoft.sqlserver.jdbc.SQLServerDriver", "jdbc:sqlserver://%s:%d;databaseName=%s");
  public static final DatabaseDriver MYSQL = new DatabaseDriver ("com.mysql.cj.jdbc.Driver", "jdbc:mysql://%s:%d/%s");
  public static final DatabaseDriver ORACLE = new DatabaseDriver ("oracle.jdbc.OracleDriver", "jdbc:oracle:thin:@%s:%d/%s");
  public static final DatabaseDriver VERTICA = new DatabaseDriver ("com.vertica.jdbc.Driver", "jdbc:vertica://%s:%d/%s");
  public static final DatabaseDriver POSTGRESQL = new DatabaseDriver ("org.postgresql.Driver", "jdbc:postgresql://%s:%d/%s");
  public static final DatabaseDriver REDSHIFT = new DatabaseDriver ("com.amazon.redshift.jdbc.Driver", "jdbc:redshift://%s:%d/%s");
  public static final DatabaseDriver SNOWFLAKE = new DatabaseDriver ("net.snowflake.client.jdbc.SnowflakeDriver", "jdbc:snowflake://%s/");
  public static final DatabaseDriver YUGABYTEDB = new DatabaseDriver ("com.yugabyte.Driver", "jdbc:yugabytedb://%s:%d/%s");
  public static final DatabaseDriver EXASOL = new DatabaseDriver ("com.exasol.jdbc.EXADriver", "jdbc:exa:%s:%d");
  public static final DatabaseDriver TERADATA = new DatabaseDriver ("com.teradata.jdbc.TeraDriver", "jdbc:teradata://%s/");

  private static Map<String, DatabaseDriver> DRIVER_BY_CLASS_NAME=  new ConcurrentHashMap<>();

  public DatabaseDriver(Class<? extends java.sql.Driver> driverClass, String urlFormatString) {
    this(driverClass.getCanonicalName(), urlFormatString);
  }
  public DatabaseDriver(String driverClassName, String urlFormatString) {
    this.driverClassName = driverClassName;
    this.urlFormatString = urlFormatString;
    DRIVER_BY_CLASS_NAME.put(driverClassName, this);
  }
  public static DatabaseDriver findByDriverClassName(String driverClassName) {
    return DRIVER_BY_CLASS_NAME.get(driverClassName);
  }
}
