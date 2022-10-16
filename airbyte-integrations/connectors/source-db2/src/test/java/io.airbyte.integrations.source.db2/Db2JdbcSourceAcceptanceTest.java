/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import java.sql.JDBCType;
import java.util.Collections;
import java.util.Set;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.Db2Container;

class Db2JdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static Set<String> TEST_TABLES = Collections.emptySet();
  private static Db2Container db;
  private JsonNode config;

  @BeforeAll
  static void init() {
    db = new Db2Container("ibmcom/db2:11.5.5.0").acceptLicense();
    db.start();

    // Db2 transforms names to upper case, so we need to use upper case name to retrieve data later.
    SCHEMA_NAME = "JDBC_INTEGRATION_TEST1";
    SCHEMA_NAME2 = "JDBC_INTEGRATION_TEST2";
    TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);
    TABLE_NAME = "ID_AND_NAME";
    TABLE_NAME_WITH_SPACES = "ID AND NAME";
    TABLE_NAME_WITHOUT_PK = "ID_AND_NAME_WITHOUT_PK";
    TABLE_NAME_COMPOSITE_PK = "FULL_NAME_COMPOSITE_PK";
    TABLE_NAME_WITHOUT_CURSOR_TYPE = "TABLE_NAME_WITHOUT_CURSOR_TYPE";
    TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE = "TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE";
    TEST_TABLES = ImmutableSet
        .of(TABLE_NAME, TABLE_NAME_WITHOUT_PK, TABLE_NAME_COMPOSITE_PK);
    COL_ID = "ID";
    COL_NAME = "NAME";
    COL_UPDATED_AT = "UPDATED_AT";
    COL_FIRST_NAME = "FIRST_NAME";
    COL_LAST_NAME = "LAST_NAME";
    COL_LAST_NAME_WITH_SPACE = "LAST NAME";
    // In Db2 PK columns must be declared with NOT NULL statement.
    COLUMN_CLAUSE_WITH_PK = "id INTEGER NOT NULL, name VARCHAR(200), updated_at DATE";
    COLUMN_CLAUSE_WITH_COMPOSITE_PK = "first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, updated_at DATE";
    // There is no IF EXISTS statement for a schema in Db2.
    // The schema name must be in the catalog when attempting the DROP statement; otherwise an error is
    // returned.
    DROP_SCHEMA_QUERY = "DROP SCHEMA %s RESTRICT";
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s boolean)";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(true)";
  }

  @BeforeEach
  public void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put("db", db.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "unencrypted")
            .build()))
        .build());

    super.setup();
  }

  @AfterEach
  public void clean() throws Exception {
    // In Db2 before dropping a schema, all objects that were in that schema must be dropped or moved to
    // another schema.
    for (final String tableName : TEST_TABLES) {
      final String dropTableQuery = String
          .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME, tableName);
      super.database.execute(connection -> connection.createStatement().execute(dropTableQuery));
    }
    for (int i = 2; i < 10; i++) {
      final String dropTableQuery = String
          .format("DROP TABLE IF EXISTS %s.%s%s", SCHEMA_NAME, TABLE_NAME, i);
      super.database.execute(connection -> connection.createStatement().execute(dropTableQuery));
    }
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITH_SPACES))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITH_SPACES + 2))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME2,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITHOUT_CURSOR_TYPE))));
    super.database.execute(connection -> connection.createStatement().execute(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            sourceOperations.enquoteIdentifier(connection, TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE))));
    super.tearDown();
  }

  @AfterAll
  static void cleanUp() {
    db.close();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  public String getDriverClass() {
    return Db2Source.DRIVER_CLASS;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new Db2Source();
  }

}
