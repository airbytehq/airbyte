package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class SnowflakeStagingSqlOperationsTest {

  public static final String SCHEMA_NAME = "schemaName";
  public static final String STAGE_NAME = "stageName";
  private final SnowflakeStagingSqlOperations snowflakeStagingSqlOperations = new SnowflakeStagingSqlOperations();

  @Test
  void createStageIfNotExists() {
    String actualCreateStageQuery = snowflakeStagingSqlOperations.getCreateStageQuery(STAGE_NAME);
    String expectedCreateStageQuery = "CREATE STAGE IF NOT EXISTS " + STAGE_NAME + " encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
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