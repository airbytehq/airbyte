// Copyright 2021-present StarRocks, Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package io.airbyte.integrations.destination.starrocks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.JavaBaseConstants;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SqlUtil {

    private static final Logger LOG = LoggerFactory.getLogger(SqlUtil.class);
    
    public static Connection createJDBCConnection(JsonNode config) throws ClassNotFoundException, SQLException {
        String dbUrl = String.format(StarRocksConstants.PATTERN_JDBC_URL,
                config.get(StarRocksConstants.KEY_FE_HOST).asText(),
                config.get(StarRocksConstants.KEY_FE_QUERY_PORT).asInt(StarRocksConstants.DEFAULT_FE_QUERY_PORT),
                config.get(StarRocksConstants.KEY_DB).asText());
        LOG.info(String.format("dbURL: %s", dbUrl));


        try {
            Class.forName(StarRocksConstants.CJ_JDBC_DRIVER);
//            Class.forName(StarRocksConstants.JDBC_DRIVER);
        } catch (ClassNotFoundException e) {
            Class.forName(StarRocksConstants.JDBC_DRIVER);
        }

        String user = config.get(StarRocksConstants.KEY_USER) == null ?
                StarRocksConstants.DEFAULT_USER :
                config.get(StarRocksConstants.KEY_USER).asText();
        String pwd = config.get(StarRocksConstants.KEY_PWD) == null ?
                StarRocksConstants.DEFAULT_PWD :
                config.get(StarRocksConstants.KEY_PWD).asText();
        LOG.info(String.format("username: %s, pwd: %s", user, pwd));

        String PATTERN_JDBC_URL_WITHOUTDB = "jdbc:mysql://%s:%d/?rewriteBatchedStatements=true&useUnicode=true&characterEncoding=utf8&autoReconnect=true&enabledTLSProtocols=TLSv1.3,TLSv1.2,TLSv1.1,TLSv1&tcpKeepalive=true";

        String dbUrlwithoutdb = String.format(PATTERN_JDBC_URL_WITHOUTDB,
        config.get(StarRocksConstants.KEY_FE_HOST).asText(),
        config.get(StarRocksConstants.KEY_FE_QUERY_PORT).asInt(StarRocksConstants.DEFAULT_FE_QUERY_PORT),
        "");
        LOG.info(String.format("dbURL-withoutDB: %s", dbUrlwithoutdb));        

        Connection conn = DriverManager.getConnection(dbUrlwithoutdb, user, pwd);
        Statement statement = conn.createStatement();
        String query = String.format("create database if not exists %s;", config.get(StarRocksConstants.KEY_DB).asText());
        LOG.info(String.format("query: %s", query));
        statement.executeUpdate(query);
        conn.close();

        return DriverManager.getConnection(dbUrl, user, pwd);
    }

    public static void execute(Connection conn, String sql) throws SQLException {
        try (Statement statement = conn.createStatement()) {
            statement.execute(sql);
        }
    }


    public static void createDatabaseIfNotExist(Connection conn, String db) throws SQLException {
        String sql = String.format("CREATE DATABASE IF NOT EXISTS %s;", db);
        LOG.info(String.format("SQL: %s", sql));
        execute(conn, sql);
    }

    public static void truncateTable(Connection conn, String tableName) throws SQLException {
        String sql = String.format("TRUNCATE TABLE %s;", tableName);
        LOG.info(String.format("SQL: %s", sql));
        execute(conn, sql);
    }

    public static void insertFromTable(Connection conn, String srcTableName, String dstTableName) throws SQLException {
        String sql = String.format("INSERT INTO %s SELECT * FROM %s;",  dstTableName, srcTableName);
        LOG.info(String.format("SQL: %s", sql));
        execute(conn, sql);
    }

    public static void renameTable(Connection conn, String srcTableName, String dstTableName) throws SQLException {
        String sql = String.format("ALTER TABLE %s RENAME %s;", srcTableName, dstTableName);
        LOG.info(String.format("SQL: %s", sql));
        execute(conn, sql);
    }

    public static void createTableIfNotExist(Connection conn, String tableName) throws SQLException {
        String sql = "CREATE TABLE IF NOT EXISTS " + tableName + " ( \n"
                + "`" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT + "` BIGINT,\n"
                + "`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "` varchar(40),\n"
                + "`" + JavaBaseConstants.COLUMN_NAME_DATA + "` String)\n"
                + "DUPLICATE KEY(`" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT + "`,`"
                + JavaBaseConstants.COLUMN_NAME_AB_ID + "`) \n"
                + "DISTRIBUTED BY HASH(`" + JavaBaseConstants.COLUMN_NAME_AB_ID + "`) BUCKETS 16 \n"
                + "PROPERTIES ( \n"
                + "\"replication_num\" = \"1\" \n"
                + ");";
                LOG.info(String.format("SQL: %s", sql));
        execute(conn, sql);
    }

    public static void dropTableIfExists(Connection conn, String tableName) throws SQLException {
        String sql = String.format("DROP TABLE IF EXISTS `%s`;", tableName);
        LOG.info(String.format("SQL: %s", sql));
        execute(conn, sql);
    }

}
