/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SelectdbOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SelectdbOperations.class);

  private static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";
  private static final String DB_URL_PATTERN = "jdbc:mysql://%s/%s?rewriteBatchedStatements=true&useUnicode=true&characterEncoding=utf8";

  // private JsonNode config;
  private Connection conn = null;

  public SelectdbOperations() {
    // this.config = config;
  }

  public Connection getConn(JsonNode config) throws SQLException, ClassNotFoundException {
    if (conn == null) {
      checkSelectdbAndConnect(config);
    }
    return conn;
  }

  public void closeConn() throws SQLException {
    if (conn != null) {
      conn.close();
    }
  }

  private void checkSelectdbAndConnect(JsonNode config) throws ClassNotFoundException, SQLException {
    SelectdbConnectionOptions selectdbConnection = SelectdbConnectionOptions.getSelectdbConnection(config, "");
    String dbUrl = String.format(DB_URL_PATTERN, selectdbConnection.getJdbcUrl(), selectdbConnection.getDb());
    Class.forName(JDBC_DRIVER);
    conn = DriverManager.getConnection(dbUrl, selectdbConnection.getUser(), selectdbConnection.getPwd());
  }

  public String truncateTable(String tableName) {
    String s = "TRUNCATE TABLE `" + tableName + "`;";
    LOGGER.info("truncate selectdb table SQL :  \n " + s);
    return s;
  }

  protected String createTableQuery(String tableName) {
    String s = "CREATE TABLE IF NOT EXISTS `" + tableName + "` ( \n"
        + "`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "` varchar(40),\n"
        + "`" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT + "` BIGINT,\n"
        + "`" + JavaBaseConstants.COLUMN_NAME_DATA + "` String)\n"
        + "DUPLICATE KEY(`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "`,`"
        + JavaBaseConstants.COLUMN_NAME_EMITTED_AT + "`) \n"
        + "DISTRIBUTED BY HASH(`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "`) BUCKETS 16 ;";
    LOGGER.info("create selectdb table SQL :  \n " + s);
    return s;
  }

}
