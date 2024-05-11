/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SnowflakeSqlOperationsTest {

  private SnowflakeSqlOperations snowflakeSqlOperations;
  public static String SCHEMA_NAME = "schemaName";
  public static final String TABLE_NAME = "tableName";
  JdbcDatabase db = mock(JdbcDatabase.class);

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(Jsons.emptyObject());
    snowflakeSqlOperations = new SnowflakeSqlOperations();
  }

  @Test
  void createTableQuery() {
    final String expectedQuery = String.format(
        """
        CREATE TABLE IF NOT EXISTS "%s"."%s" (
          "%s" VARCHAR PRIMARY KEY,
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
          "%s" VARIANT
        ) data_retention_time_in_days = 1;""",
        SCHEMA_NAME,
        TABLE_NAME,
        JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
        JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
        JavaBaseConstants.COLUMN_NAME_DATA);
    final String actualQuery = snowflakeSqlOperations.createTableQuery(db, SCHEMA_NAME, TABLE_NAME);
    assertEquals(expectedQuery, actualQuery);
  }

  @Test
  void isSchemaExists() throws Exception {
    snowflakeSqlOperations.isSchemaExists(db, SCHEMA_NAME);
    verify(db, times(1)).unsafeQuery(anyString());
  }

  @Test
  void insertRecordsInternal() throws SQLException {
    snowflakeSqlOperations.insertRecordsInternal(db, List.of(new PartialAirbyteMessage()), SCHEMA_NAME, TABLE_NAME);
    verify(db, times(1)).execute(any(CheckedConsumer.class));
  }

}
