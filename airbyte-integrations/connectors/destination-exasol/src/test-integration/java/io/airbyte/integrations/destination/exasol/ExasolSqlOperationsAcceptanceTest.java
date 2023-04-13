/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.exasol.containers.ExasolContainer;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLSyntaxErrorException;
import java.util.Arrays;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ExasolSqlOperationsAcceptanceTest {

  private static final ExasolContainer<? extends ExasolContainer<?>> EXASOL = new ExasolContainer<>()
      .withReuse(true);
  private ExasolSqlOperations operations;

  @BeforeAll
  static void startExasolContainer() {
    EXASOL.start();
  }

  @AfterAll
  static void stopExasolContainer() {
    EXASOL.stop();
  }

  @BeforeEach
  void setup() {
    this.operations = new ExasolSqlOperations();
    EXASOL.purgeDatabase();
  }

  @Test
  void executeTransactionEmptyList() {
    assertDoesNotThrow(() -> executeTransaction());
  }

  @Test
  void executeTransactionSingleStatementSuccess() throws Exception {
    executeTransaction("CREATE SCHEMA TESTING_SCHEMA");
    assertSchemaExists("TESTING_SCHEMA", true);
  }

  @Test
  void executeTransactionTowStatementsSuccess() throws Exception {
    executeTransaction("CREATE SCHEMA TESTING_SCHEMA", "CREATE TABLE TESTING_TABLE (C1 VARCHAR(5))");
    assertSchemaExists("TESTING_SCHEMA", true);
    assertTableExists("TESTING_SCHEMA", "TESTING_TABLE");
  }

  @Test
  void executeTransactionTwoStatementsFailure() throws Exception {
    assertThrows(SQLSyntaxErrorException.class, () -> executeTransaction("CREATE SCHEMA TESTING_SCHEMA", "INVALID STATEMENT"));
    assertSchemaExists("TESTING_SCHEMA", false);
  }

  private static void assertSchemaExists(String schemaName, boolean exists) throws SQLException {
    try (ResultSet rs = EXASOL.createConnection().getMetaData().getSchemas(null, schemaName)) {
      assertThat("Schema exists", rs.next(), equalTo(exists));
    }
  }

  private static void assertTableExists(String schemaName, String tableName) throws SQLException {
    try (ResultSet rs = EXASOL.createConnection().getMetaData().getTables(null, schemaName, tableName, null)) {
      assertThat("Table exists", rs.next(), equalTo(true));
    }
  }

  private void executeTransaction(String... statements) throws Exception {
    this.operations.executeTransaction(createDatabase(), Arrays.asList(statements));
  }

  private JdbcDatabase createDatabase() {
    DataSource dataSource = DataSourceFactory.create(EXASOL.getUsername(), EXASOL.getPassword(), ExasolDestination.DRIVER_CLASS, EXASOL.getJdbcUrl());
    return new DefaultJdbcDatabase(dataSource);
  }

}
