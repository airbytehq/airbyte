/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableSet;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import java.util.Collections;
import java.util.Set;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.containers.Db2Container;

@Disabled
class Db2JdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<Db2Source, Db2TestDatabase> {

  private final static Db2Container DB_2_CONTAINER = new Db2Container("ibmcom/db2:11.5.5.0").acceptLicense();
  private static final String QUOTE_STRING = "\"";
  private static Set<String> TEST_TABLES = Collections.emptySet();

  @BeforeAll
  static void init() {
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
    TABLE_NAME_AND_TIMESTAMP = "NAME_AND_TIMESTAMP";
    TEST_TABLES = ImmutableSet
        .of(TABLE_NAME, TABLE_NAME_WITHOUT_PK, TABLE_NAME_COMPOSITE_PK, TABLE_NAME_AND_TIMESTAMP);
    COL_ID = "ID";
    COL_NAME = "NAME";
    COL_UPDATED_AT = "UPDATED_AT";
    COL_FIRST_NAME = "FIRST_NAME";
    COL_LAST_NAME = "LAST_NAME";
    COL_LAST_NAME_WITH_SPACE = "LAST NAME";
    COL_TIMESTAMP = "TIMESTAMP";
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

  @AfterAll
  static void cleanUp() {
    DB_2_CONTAINER.close();
  }

  static void deleteTablesAndSchema(final Db2TestDatabase testdb) {
    // In Db2 before dropping a schema, all objects that were in that schema must be dropped or moved to
    // another schema.
    for (final String tableName : TEST_TABLES) {
      final String dropTableQuery = String
          .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME, tableName);
      testdb.with(dropTableQuery);
    }
    for (int i = 2; i < 10; i++) {
      final String dropTableQuery = String
          .format("DROP TABLE IF EXISTS %s.%s%s", SCHEMA_NAME, TABLE_NAME, i);
      testdb.with(dropTableQuery);
    }
    testdb.with(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            enquoteIdentifier(TABLE_NAME_WITH_SPACES, QUOTE_STRING)));
    testdb.with(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            enquoteIdentifier(TABLE_NAME_WITH_SPACES + 2, QUOTE_STRING)));
    testdb.with(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME2,
            enquoteIdentifier(TABLE_NAME, QUOTE_STRING)));
    testdb.with(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            enquoteIdentifier(TABLE_NAME_WITHOUT_CURSOR_TYPE, QUOTE_STRING)));
    testdb.with(String
        .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME,
            enquoteIdentifier(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE, QUOTE_STRING)));
    for (final String schemaName : TEST_SCHEMAS) {
      testdb.with(DROP_SCHEMA_QUERY, schemaName);
    }

  }

  @Override
  protected Db2TestDatabase createTestDatabase() {
    DB_2_CONTAINER.start();
    return new Db2TestDatabase(DB_2_CONTAINER).initialized();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public JsonNode config() {
    return Jsons.clone(testdb.configBuilder().build());
  }

  @Override
  protected Db2Source source() {
    return new Db2Source();
  }

}
