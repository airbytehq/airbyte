/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class SnowflakeInternalStagingSqlOperationsTest {

  public static final String SCHEMA_NAME = "schemaName";
  public static final String STAGE_NAME = "stageName";
  private final SnowflakeInternalStagingSqlOperations snowflakeStagingSqlOperations =
      new SnowflakeInternalStagingSqlOperations(new SnowflakeSQLNameTransformer());

  @Test
  void createStageIfNotExists() {
    String actualCreateStageQuery = snowflakeStagingSqlOperations.getCreateStageQuery(STAGE_NAME);
    String expectedCreateStageQuery =
        "CREATE STAGE IF NOT EXISTS " + STAGE_NAME + " encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
    assertEquals(expectedCreateStageQuery, actualCreateStageQuery);
  }

  @Test
  void copyIntoTmpTableFromStage() {
    String expectedQuery = "COPY INTO schemaName.tableName FROM @stageName file_format = " +
        "(type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')";
    String actualCopyQuery = snowflakeStagingSqlOperations.getCopyQuery(STAGE_NAME, "tableName", SCHEMA_NAME);
    assertEquals(expectedQuery, actualCopyQuery);
  }

  @Test
  void dropStageIfExists() {
    String expectedQuery = "DROP STAGE IF EXISTS " + STAGE_NAME + ";";
    String actualDropQuery = snowflakeStagingSqlOperations.getDropQuery(STAGE_NAME);
    assertEquals(expectedQuery, actualDropQuery);
  }

}
