/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.DestinationConfig;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SnowflakeBulkLoadSqlOperationsTest {

  private static final String SCHEMA_NAME = "schemaName";
  private static final String STAGE_NAME = "stageName";
  private static final String FILE_FORMAT_NAME = "my_file_format";
  private static final String FILE_PATH = "filepath/filename";

  private SnowflakeBulkLoadSqlOperations snowflakeBulkLoadSqlOperations;

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(Jsons.emptyObject());
    snowflakeBulkLoadSqlOperations =
        new SnowflakeBulkLoadSqlOperations(new SnowflakeSQLNameTransformer());
  }

  @Test
  public void getRelativePath_WithValidRoot_ReturnsRelativePath() throws Exception {
    String rootPath = "s3:/bucket-name/path/prefix";
    String s3Path = "s3:/bucket-name/path/prefix/folder/file.txt";
    String relativePath = SnowflakeBulkLoadDestination.getRelativePath(rootPath, s3Path);
    assertEquals("/folder/file.txt", relativePath);
  }

  @Test
  public void getRelativePath_WithInvalidRoot_ThrowsException() {
    String rootPath = "s3:/wrong-bucket-name/path/prefix";
    String s3Path = "s3:/bucket-name/path/prefix/folder/file.txt";
    assertThrows(SnowflakeBulkLoadDestination.InvalidValueException.class, () -> {
      SnowflakeBulkLoadDestination.getRelativePath(rootPath, s3Path);
    });
  }

  @Test
  void listStage() {
    final String expectedQuery = "LIST @" + STAGE_NAME + "/" + "" + FILE_PATH + ";";
    final String actualListQuery = snowflakeBulkLoadSqlOperations.getListQuery(STAGE_NAME, "", FILE_PATH);
    assertEquals(expectedQuery, actualListQuery);
  }

  @Test
  void testCopySQLStatement() {
    final String expectedQuery =
        """
        COPY INTO "schemaName"."tableName" FROM '@stageName/'
        file_format = my_file_format
         files = ('filename1.csv','filename2.csv','filename3.csv');""";
    final List<String> fileList = List.of(
        "s3://my-bucket/root/path/filename1.csv",
        "s3://my-bucket/root/path/filename2.csv",
        "s3://my-bucket/root/path/filename3.csv");
    final String actualCopyQuery =
        snowflakeBulkLoadSqlOperations.getCopyQuery(STAGE_NAME, fileList, "tableName", SCHEMA_NAME, FILE_FORMAT_NAME);
    assertEquals(expectedQuery, actualCopyQuery);
  }

}
