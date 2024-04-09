/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SnowflakeInternalStagingSqlOperationsTest {

  private static final String SCHEMA_NAME = "schemaName";
  private static final String STAGE_NAME = "stageName";
  private static final String STAGE_PATH = "stagePath/2022/";
  private static final String FILE_PATH = "filepath/filename";

  private SnowflakeInternalStagingSqlOperations snowflakeStagingSqlOperations;

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(Jsons.emptyObject());
    snowflakeStagingSqlOperations =
        new SnowflakeInternalStagingSqlOperations(new SnowflakeSQLNameTransformer());
  }

  @Test
  void createStageIfNotExists() {
    final String actualCreateStageQuery = snowflakeStagingSqlOperations.getCreateStageQuery(STAGE_NAME);
    final String expectedCreateStageQuery =
        "CREATE STAGE IF NOT EXISTS " + STAGE_NAME + " encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
    assertEquals(expectedCreateStageQuery, actualCreateStageQuery);
  }

  @Test
  void putFileToStage() {
    final String expectedQuery = "PUT file://" + FILE_PATH + " @" + STAGE_NAME + "/" + STAGE_PATH + " PARALLEL =";
    final String actualPutQuery = snowflakeStagingSqlOperations.getPutQuery(STAGE_NAME, STAGE_PATH, FILE_PATH);
    assertTrue(actualPutQuery.startsWith(expectedQuery));
  }

  @Test
  void listStage() {
    final String expectedQuery = "LIST @" + STAGE_NAME + "/" + STAGE_PATH + FILE_PATH + ";";
    final String actualListQuery = snowflakeStagingSqlOperations.getListQuery(STAGE_NAME, STAGE_PATH, FILE_PATH);
    assertEquals(expectedQuery, actualListQuery);
  }

  @Test
  void copyIntoTmpTableFromStage() {
    final String expectedQuery =
        """
        COPY INTO "schemaName"."tableName" FROM '@stageName/stagePath/2022/'
        file_format = (
          type = csv
          compression = auto
          field_delimiter = ','
          skip_header = 0
          FIELD_OPTIONALLY_ENCLOSED_BY = '"'
          NULL_IF=('')
          error_on_column_count_mismatch=false
        ) files = ('filename1','filename2');""";
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

  @Test
  void removeStage() {
    final String expectedQuery = "REMOVE @" + STAGE_NAME + ";";
    final String actualRemoveQuery = snowflakeStagingSqlOperations.getRemoveQuery(STAGE_NAME);
    assertEquals(expectedQuery, actualRemoveQuery);
  }

}
