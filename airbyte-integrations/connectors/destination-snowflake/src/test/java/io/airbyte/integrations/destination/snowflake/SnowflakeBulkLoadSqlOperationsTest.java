/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.DestinationConfig;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SnowflakeBulkLoadSqlOperationsTest {

  private static final String SCHEMA_NAME = "schemaName";
  private static final String STAGE_NAME = "stageName";
  private static final String STAGE_PATH = "stagePath/2022/";
  private static final String FILE_PATH = "filepath/filename";

  private SnowflakeBulkLoadSqlOperations snowflakeBulkLoadSqlOperations;

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(Jsons.emptyObject());
    snowflakeBulkLoadSqlOperations =
        new SnowflakeBulkLoadSqlOperations(new SnowflakeSQLNameTransformer());
  }

  @Test
  void putFileToStage() {
    final String expectedQuery = "PUT file://" + FILE_PATH + " @" + STAGE_NAME + "/" + STAGE_PATH + " PARALLEL =";
    final String actualPutQuery = snowflakeBulkLoadSqlOperations.getPutQuery(STAGE_NAME, STAGE_PATH, FILE_PATH);
    assertTrue(actualPutQuery.startsWith(expectedQuery));
  }

  @Test
  void listStage() {
    final String expectedQuery = "LIST @" + STAGE_NAME + "/" + STAGE_PATH + FILE_PATH + ";";
    final String actualListQuery = snowflakeBulkLoadSqlOperations.getListQuery(STAGE_NAME, STAGE_PATH, FILE_PATH);
    assertEquals(expectedQuery, actualListQuery);
  }

  @Test
  void copyIntoTmpTableFromStage() {
    final String expectedQuery =
        """
        COPY INTO schemaName.tableName FROM '@s3_stage_name/'
        file_format = MY_FILE_FORMAT files = ('filename1','filename2');""";
    final String actualCopyQuery =
        snowflakeBulkLoadSqlOperations.getCopyQuery(STAGE_NAME, STAGE_PATH, List.of("filename1", "filename2"), "tableName", SCHEMA_NAME);
    assertEquals(expectedQuery, actualCopyQuery);
  }

}
