/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

import com.fasterxml.jackson.databind.JsonNode;

public class DorisConnectionOptions {

  private String db;
  private static String DB_KEY = "database";
  private String table;
  private static final String TABLE_KEY = "table";

  private String user;
  private static final String USER_KEY = "username";

  private String pwd;
  private static final String PWD_KEY = "password";

  private String feHost;
  private static final String FE_HOST_KEY = "host";

  private Integer feHttpPort;
  private static final String FE_HTTP_PORT_KEY = "httpport";

  private Integer feQueryPort;
  private static final String FE_QUERY_PORT_KEY = "queryport";

  public static DorisConnectionOptions getDorisConnection(final JsonNode config, String table) {
    return new DorisConnectionOptions(
        config.get(DB_KEY).asText(),
        table,
        config.get(USER_KEY).asText(),
        config.get(PWD_KEY) == null ? "" : config.get(PWD_KEY).asText(),
        config.get(FE_HOST_KEY).asText(),
        config.get(FE_HTTP_PORT_KEY).asInt(8030),
        config.get(FE_QUERY_PORT_KEY).asInt(9030));

  }

  public DorisConnectionOptions(String db, String table, String user, String pwd, String feHost, Integer feHttpPort, Integer feQueryPort) {
    this.db = db;
    this.table = table;
    this.user = user;
    this.pwd = pwd;
    this.feHost = feHost;
    this.feHttpPort = feHttpPort;
    this.feQueryPort = feQueryPort;
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

  public String getFeHost() {
    return feHost;
  }

  public Integer getFeHttpPort() {
    return feHttpPort;
  }

  public String getHttpHostPort() {
    return feHost + ":" + feHttpPort;
  }

  public String getQueryHostPort() {
    return feHost + ":" + feHttpPort;
  }

  public Integer getFeQueryPort() {
    return feQueryPort;
  }

  @Override
  public String toString() {
    return "DorisConnectionOptions{" +
        "db='" + db + '\'' +
        ", table='" + table + '\'' +
        ", user='" + user + '\'' +
        ", pwd='" + pwd + '\'' +
        ", feHost='" + feHost + '\'' +
        ", feHttpPort=" + feHttpPort +
        ", feQueryPort=" + feQueryPort +
        '}';
  }

}
