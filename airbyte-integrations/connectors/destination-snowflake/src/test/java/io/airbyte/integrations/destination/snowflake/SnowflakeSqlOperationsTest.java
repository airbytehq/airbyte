/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

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

}
