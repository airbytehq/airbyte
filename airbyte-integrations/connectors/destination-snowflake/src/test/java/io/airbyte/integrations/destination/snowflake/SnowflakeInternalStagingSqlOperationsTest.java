/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.SQLException;
import java.util.List;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.Mockito;

class SnowflakeInternalStagingSqlOperationsTest {

  private static final String SCHEMA_NAME = "schemaName";
  private static final String STAGE_NAME = "stageName";
  private static final String STAGE_PATH = "stagePath/2022/";
  private static final String FILE_PATH = "filepath/filename";

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
    final String expectedQuery = "COPY INTO schemaName.tableName FROM '@" + STAGE_NAME + "/" + STAGE_PATH + "' "
        + "file_format = (type = csv compression = auto field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') "
        + "files = ('filename1','filename2');";
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

  @ParameterizedTest
  @CsvSource({"TEST,false", "but current role has no privileges on it,true"})
  public void testCreateStageIfNotExists(final String message, final boolean shouldCapture) {
    final JdbcDatabase db = Mockito.mock(JdbcDatabase.class);
    final String stageName = "foo";
    try {
      Mockito.doThrow(new SnowflakeSQLException(message)).when(db).execute(Mockito.anyString());
    } catch (SQLException e) {
      // This would not be expected, but the `execute` method above will flag as an unhandled exception
      assert false;
    }
    final Exception exception = Assertions.assertThrows(Exception.class, () -> snowflakeStagingSqlOperations.createStageIfNotExists(db, stageName));
    if (shouldCapture) {
      assertInstanceOf(ConfigErrorException.class, exception);
    } else {
      assertInstanceOf(SnowflakeSQLException.class, exception);
      assertEquals(exception.getMessage(), message);
    }
  }

}
