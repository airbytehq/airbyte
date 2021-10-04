/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import static org.junit.Assert.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.OracleContainer;

class OracleJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleJdbcSourceAcceptanceTest.class);
  private static OracleContainer ORACLE_DB;

  @BeforeAll
  static void init() {
    // Oracle returns uppercase values

    ORACLE_DB = new OracleContainer("epiclabs/docker-oracle-xe-11g")
        .withEnv("NLS_DATE_FORMAT", "YYYY-MM-DD");
    ORACLE_DB.start();
  }

  @BeforeEach
  public void setup() throws Exception {

    SCHEMA_NAME = "JDBC_INTEGRATION_TEST1";
    SCHEMA_NAME2 = "JDBC_INTEGRATION_TEST2";
    TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);

    TABLE_NAME = "ID_AND_NAME";
    TABLE_NAME_WITH_SPACES = "ID AND NAME";
    TABLE_NAME_WITHOUT_PK = "ID_AND_NAME_WITHOUT_PK";
    TABLE_NAME_COMPOSITE_PK = "FULL_NAME_COMPOSITE_PK";
    COL_ID = "ID";
    COL_NAME = "NAME";
    COL_UPDATED_AT = "UPDATED_AT";
    COL_FIRST_NAME = "FIRST_NAME";
    COL_LAST_NAME = "LAST_NAME";
    COL_LAST_NAME_WITH_SPACE = "LAST NAME";
    ID_VALUE_1 = new BigDecimal(1);
    ID_VALUE_2 = new BigDecimal(2);
    ID_VALUE_3 = new BigDecimal(3);
    ID_VALUE_4 = new BigDecimal(4);
    ID_VALUE_5 = new BigDecimal(5);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", ORACLE_DB.getHost())
        .put("port", ORACLE_DB.getFirstMappedPort())
        .put("sid", ORACLE_DB.getSid())
        .put("username", ORACLE_DB.getUsername())
        .put("password", ORACLE_DB.getPassword())
        .put("schemas", List.of(SCHEMA_NAME, SCHEMA_NAME2))
        .build());

    // Because Oracle doesn't let me create database easily I need to clean up
    cleanUpTables();

    super.setup();
  }

  @AfterEach
  public void tearDownOracle() throws Exception {
    // ORA-12519
    // https://stackoverflow.com/questions/205160/what-can-cause-intermittent-ora-12519-tns-no-appropriate-handler-found-errors
    // sleep for 1000
    executeOracleStatement(String.format("DROP TABLE %s", getFullyQualifiedTableName(TABLE_NAME)));
    executeOracleStatement(
        String.format("DROP TABLE %s", getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));
    executeOracleStatement(
        String.format("DROP TABLE %s", getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));
    Thread.sleep(1000);
  }

  void cleanUpTables() throws SQLException {
    final Connection conn = DriverManager.getConnection(
        ORACLE_DB.getJdbcUrl(),
        ORACLE_DB.getUsername(),
        ORACLE_DB.getPassword());
    for (final String schemaName : TEST_SCHEMAS) {
      final ResultSet resultSet =
          conn.createStatement().executeQuery(String.format("SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = '%s'", schemaName));
      while (resultSet.next()) {
        String tableName = resultSet.getString("TABLE_NAME");
        String tableNameProcessed = tableName.contains(" ") ? sourceOperations
            .enquoteIdentifier(conn, tableName) : tableName;
        conn.createStatement().executeQuery(String.format("DROP TABLE %s.%s", schemaName, tableNameProcessed));
      }
    }
    if (!conn.isClosed())
      conn.close();
  }

  @Override
  public boolean supportsSchemas() {
    // See https://www.oratable.com/oracle-user-schema-difference/
    return true;
  }

  @Override
  public AbstractJdbcSource getJdbcSource() {
    return new OracleSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return OracleSource.DRIVER_CLASS;
  }

  @AfterAll
  static void cleanUp() {
    ORACLE_DB.close();
  }

  @Override
  public void createSchemas() throws SQLException {
    // In Oracle, `CREATE USER` creates a schema.
    // See https://www.oratable.com/oracle-user-schema-difference/
    if (supportsSchemas()) {
      for (final String schemaName : TEST_SCHEMAS) {
        executeOracleStatement(
            String.format(
                "CREATE USER %s IDENTIFIED BY password DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS",
                schemaName));
      }
    }
  }

  public void executeOracleStatement(final String query) throws SQLException {
    final Connection conn = DriverManager.getConnection(
        ORACLE_DB.getJdbcUrl(),
        ORACLE_DB.getUsername(),
        ORACLE_DB.getPassword());
    try (final Statement stmt = conn.createStatement()) {
      stmt.execute(query);
    } catch (final SQLException e) {
      logSQLException(e);
    }
    conn.close();
  }

  public static void logSQLException(final SQLException ex) {
    for (final Throwable e : ex) {
      if (e instanceof SQLException) {
        if (ignoreSQLException(((SQLException) e).getSQLState()) == false) {
          e.printStackTrace(System.err);
          LOGGER.info("SQLState: " + ((SQLException) e).getSQLState());
          LOGGER.info("Error Code: " + ((SQLException) e).getErrorCode());
          LOGGER.info("Message: " + e.getMessage());
          Throwable t = ex.getCause();
          while (t != null) {
            LOGGER.info("Cause: " + t);
            t = t.getCause();
          }
        }
      }
    }
  }

  public static boolean ignoreSQLException(final String sqlState) {
    // This only ignore cases where other databases won't raise errors
    // Drop table, schema etc or try to recreate a table;
    if (sqlState == null) {
      LOGGER.info("The SQL state is not defined!");
      return false;
    }
    // X0Y32: Jar file already exists in schema
    if (sqlState.equalsIgnoreCase("X0Y32")) {
      return true;
    }
    // 42Y55: Table already exists in schema
    if (sqlState.equalsIgnoreCase("42Y55")) {
      return true;
    }
    // 42000: User name already exists
    if (sqlState.equalsIgnoreCase("42000")) {
      return true;
    }

    return false;
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

}
