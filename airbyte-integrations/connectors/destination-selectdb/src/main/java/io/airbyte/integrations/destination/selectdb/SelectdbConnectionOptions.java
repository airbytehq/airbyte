/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;

public class SelectdbConnectionOptions {

  protected final String driverName = "com.mysql.jdbc.Driver";
  protected final String cjDriverName = "com.mysql.cj.jdbc.Driver";

  private String db;
  private static String DB_KEY = "database";

  private String table;
  private static final String TABLE_KEY = "table";

  private String user;
  private static final String USER_KEY = "user_name";

  private String pwd;
  private static final String PWD_KEY = "password";

  private String loadUrl;
  private static final String LOAD_URL_KEY = "load_url";

  private String jdbcUrl;
  private static final String JDBC_URL_KEY = "jdbc_url";

  private String clusterName;
  private static final String CLUSTER_NAME_KEY = "cluster_name";

  public static SelectdbConnectionOptions getSelectdbConnection(final JsonNode config, String table) {
    return new SelectdbConnectionOptions(
        config.get(DB_KEY).asText(),
        table,
        config.get(LOAD_URL_KEY).asText(),
        config.get(JDBC_URL_KEY).asText(),
        config.get(CLUSTER_NAME_KEY).asText(),
        config.get(USER_KEY).asText(),
        config.get(PWD_KEY) == null ? "" : config.get(PWD_KEY).asText());

  }

  public SelectdbConnectionOptions(String db,
                                   String table,
                                   String loadUrl,
                                   String jdbcUrl,
                                   String clusterName,
                                   String username,
                                   String password) {
    this.db = db;
    this.table = table;
    this.loadUrl = Preconditions.checkNotNull(loadUrl, "loadUrl  is empty");
    this.jdbcUrl = Preconditions.checkNotNull(jdbcUrl, "jdbcUrl  is empty");
    this.clusterName = Preconditions.checkNotNull(clusterName, "clusterName is empty");
    this.user = username;
    this.pwd = password;
  }

  public String getLoadUrl() {
    return loadUrl;
  }

  public String getJdbcUrl() {
    return jdbcUrl;
  }

  public String getClusterName() {
    return clusterName;
  }

  public String getDb() {
    return db;
  }

  public String getTable() {
    return table;
  }

  public String getUser() {
    return user;
  }

  public String getPwd() {
    return pwd;
  }

  public String getCjDriverName() {
    return cjDriverName;
  }

  public String getDriverName() {
    return driverName;
  }

  @Override
  public String toString() {
    return "SelectdbConnectionOptions{" +
        "driverName='" + driverName + '\'' +
        ", cjDriverName='" + cjDriverName + '\'' +
        ", db='" + db + '\'' +
        ", table='" + table + '\'' +
        ", user='" + user + '\'' +
        ", pwd='" + pwd + '\'' +
        ", loadUrl='" + loadUrl + '\'' +
        ", jdbcUrl='" + jdbcUrl + '\'' +
        ", clusterName='" + clusterName + '\'' +
        '}';
  }

}
