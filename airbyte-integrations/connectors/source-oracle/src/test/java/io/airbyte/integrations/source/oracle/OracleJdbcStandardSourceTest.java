/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceStandardTest;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import static org.junit.Assert.assertEquals;

import org.testcontainers.containers.OracleContainer;

import java.sql.*;
import java.util.Set;

class OracleJdbcStandardSourceTest extends JdbcSourceStandardTest {
  private static final String SCHEMA_NAME = "JDBC_INTEGRATION_TEST";
  private static final String SCHEMA_NAME2 = "JDBC_INTEGRATION_TEST2";
  private static final Set<String> TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);
  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSource.class);
  private static OracleContainer ORACLE_DB;

  private JsonNode config;

  @BeforeAll
  static void init() throws SQLException {
    ORACLE_DB = new OracleContainer("epiclabs/docker-oracle-xe-11g");
    ORACLE_DB.start();
    }

  @BeforeEach
  public void setup() throws Exception {

    config = Jsons.jsonNode(ImmutableMap.builder()
            .put("host", ORACLE_DB.getHost())
            .put("port", ORACLE_DB.getFirstMappedPort())
            .put("sid", ORACLE_DB.getSid())
            .put("username", ORACLE_DB.getUsername())
            .put("password", ORACLE_DB.getPassword())
            .build());

    //executeOracleStatement("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'");

    super.setup();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public AbstractJdbcSource getSource() {
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
  public void createSchemas() {
      if (supportsSchemas()) {
          for (String schemaName : TEST_SCHEMAS) {
              try {
                  final String SchemaQuery = String.format("CREATE USER %s IDENTIFIED BY %s DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS", schemaName, schemaName);
                  executeOracleStatement(SchemaQuery);
              } catch (SQLException e) {
                  printSQLException(e);
              }
          }
      }
  }

  public void executeOracleStatement(String query) throws SQLException {
      Connection conn = DriverManager.getConnection(
              ORACLE_DB.getJdbcUrl(),
              ORACLE_DB.getUsername(),
              ORACLE_DB.getPassword()
      );
      try (Statement stmt = conn.createStatement()){
          stmt.execute(query);
      } catch (SQLException e) {
          printSQLException(e);
      }
  }

  public static void printSQLException(SQLException ex) {
        for (Throwable e : ex) {
            if (e instanceof SQLException) {
                if (ignoreSQLException(((SQLException)e).getSQLState()) == false) {
                    e.printStackTrace(System.err);
                    System.err.println("SQLState: " + ((SQLException)e).getSQLState());
                    System.err.println("Error Code: " + ((SQLException)e).getErrorCode());
                    System.err.println("Message: " + e.getMessage());
                    Throwable t = ex.getCause();
                    while (t != null) {
                        System.out.println("Cause: " + t);
                        t = t.getCause();
                    }
                }
            }
        }
    }

    public static boolean ignoreSQLException(String sqlState) {
        if (sqlState == null) {
            System.out.println("The SQL state is not defined!");
            return false;
        }
        // X0Y32: Jar file already exists in schema
        if (sqlState.equalsIgnoreCase("X0Y32"))
            return true;
        // 42Y55: Table already exists in schema
        if (sqlState.equalsIgnoreCase("42Y55"))
            return true;
        // 42000: User name already exists
        if (sqlState.equalsIgnoreCase("42000"))
            return true;

        return false;
    }
}
