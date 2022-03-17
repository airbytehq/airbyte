/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import org.junit.jupiter.api.Test;

class SnowflakeInternalStagingSqlOperationsTest {

  private static final String SCHEMA_NAME = "schemaName";
  private static final String STAGE_NAME = "stageName";
  private static final String STAGE_PATH = "stagePath";

  private final SnowflakeInternalStagingSqlOperations snowflakeStagingSqlOperations =
      new SnowflakeInternalStagingSqlOperations(new SnowflakeSQLNameTransformer());

  @Test
  void createStageIfNotExists() {
    final String actualCreateStageQuery = snowflakeStagingSqlOperations.getCreateStageQuery(STAGE_NAME);
    final String expectedCreateStageQuery =
        "CREATE STAGE IF NOT EXISTS " + STAGE_NAME + " encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
    assertEquals(expectedCreateStageQuery, actualCreateStageQuery);
  }

  @Test
  void copyIntoTmpTableFromStage() {
    final String expectedQuery = "COPY INTO schemaName.tableName FROM @stageName/stagePath file_format = " +
        "(type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') " +
        "files = ('filename1','filename2') ;";
    final String actualCopyQuery =
        snowflakeStagingSqlOperations.getCopyQuery(STAGE_NAME, STAGE_PATH, List.of("filename1", "filename2"), "tableName", SCHEMA_NAME);
    assertEquals(expectedQuery, actualCopyQuery);
  }

  @Test
  void dropStageIfExists() {
    final String expectedQuery = "DROP STAGE IF EXISTS " + STAGE_NAME + ";";
    final String actualDropQuery = snowflakeStagingSqlOperations.getDropQuery(STAGE_NAME);
    assertEquals(expectedQuery, actualDropQuery);
  }

}
