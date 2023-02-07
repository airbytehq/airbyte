/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.Mockito;

class SnowflakeSqlOperationsTest {

  SnowflakeSqlOperations snowflakeSqlOperations = new SnowflakeSqlOperations();
  public static String SCHEMA_NAME = "schemaName";
  public static final String TABLE_NAME = "tableName";
  List<AirbyteRecordMessage> records = new ArrayList<>();
  JdbcDatabase db = mock(JdbcDatabase.class);

  @Test
  void createTableQuery() {
    String expectedQuery = String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s VARIANT,\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()\n"
            + ") data_retention_time_in_days = 0;",
        SCHEMA_NAME, TABLE_NAME, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    String actualQuery = snowflakeSqlOperations.createTableQuery(db, SCHEMA_NAME, TABLE_NAME);
    assertEquals(expectedQuery, actualQuery);
  }

  @Test
  void isSchemaExists() throws Exception {
    snowflakeSqlOperations.isSchemaExists(db, SCHEMA_NAME);
    verify(db, times(1)).unsafeQuery(anyString());
  }

  @Test
  void insertRecordsInternal() throws SQLException {
    snowflakeSqlOperations.insertRecordsInternal(db, List.of(new AirbyteRecordMessage()), SCHEMA_NAME, TABLE_NAME);
    verify(db, times(1)).execute(any(CheckedConsumer.class));
  }

  @ParameterizedTest
  @CsvSource({"TEST,false", "but current role has no privileges on it,true"})
  public void testCreateSchemaIfNotExists(final String message, final boolean shouldCapture) {
    final JdbcDatabase db = Mockito.mock(JdbcDatabase.class);
    final var schemaName = "foo";
    try {
      Mockito.doThrow(new SnowflakeSQLException(message)).when(db).execute(Mockito.anyString());
    } catch (Exception e) {
      // This would not be expected, but the `execute` method above will flag as an unhandled exception
      assert false;
    }
    Exception exception = assertThrows(Exception.class, () -> snowflakeSqlOperations.createSchemaIfNotExists(db, schemaName));
    if (shouldCapture) {
      assertInstanceOf(ConfigErrorException.class, exception);
    } else {
      assertInstanceOf(SnowflakeSQLException.class, exception);
      assertEquals(exception.getMessage(), message);
    }
  }

  @ParameterizedTest
  @CsvSource({"TEST,false", "but current role has no privileges on it,true"})
  public void testCreateTableIfNotExists(final String message, final boolean shouldCapture) {
    final JdbcDatabase db = Mockito.mock(JdbcDatabase.class);
    final String schemaName = "foo";
    final String tableName = "bar";
    try {
      Mockito.doThrow(new SnowflakeSQLException(message)).when(db).execute(Mockito.anyString());
    } catch (SQLException e) {
      // This would not be expected, but the `execute` method above will flag as an unhandled exception
      assert false;
    }
    final Exception exception =
        assertThrows(Exception.class, () -> snowflakeSqlOperations.createTableIfNotExists(db, schemaName, tableName));
    if (shouldCapture) {
      assertInstanceOf(ConfigErrorException.class, exception);
    } else {
      assertInstanceOf(SnowflakeSQLException.class, exception);
      assertEquals(exception.getMessage(), message);
    }
  }

}
