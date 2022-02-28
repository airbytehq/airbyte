package io.airbyte.integrations.destination.snowflake;

import static net.snowflake.client.loader.LoaderProperty.schemaName;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class SnowflakeStagingSqlOperationsTest {

  public static final String SCHEMA_NAME = "schemaName";
  public static final String STAGE_NAME = "stageName";
  private List<AirbyteRecordMessage> records = new ArrayList<>();
  private JdbcDatabase db = mock(JdbcDatabase.class);
  private SnowflakeStagingSqlOperations snowflakeStagingSqlOperations = new SnowflakeStagingSqlOperations();

  @Test
  void insertEmptyRecordsInternal() throws SQLException {
    snowflakeStagingSqlOperations.insertRecordsInternal(db, records, SCHEMA_NAME, STAGE_NAME);
    verify(db, never()).execute(anyString());
  }

  @Test
  void insertRecordsInternal() throws SQLException {
    records.add(mock(AirbyteRecordMessage.class));
    snowflakeStagingSqlOperations.insertRecordsInternal(db, records, SCHEMA_NAME, STAGE_NAME);
    verify(db, times(1)).execute(anyString());
  }

  @Test
  void createStageIfNotExists() throws SQLException {
    snowflakeStagingSqlOperations.createStageIfNotExists(db, STAGE_NAME);
    String expectedQuery = String.format(
        "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');", STAGE_NAME);
    verify(db, times(1)).execute(expectedQuery);
  }

  @Test
  void copyIntoTmpTableFromStage() throws SQLException {
    String tableName = "tableName";
    snowflakeStagingSqlOperations.copyIntoTmpTableFromStage(db, STAGE_NAME, tableName, SCHEMA_NAME);

    String query = String.format("COPY INTO %s.%s FROM @%s file_format = " +
            "(type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')",
        schemaName, tableName, STAGE_NAME);
    verify(db, times(1)).execute(query);
  }

  @Test
  void dropStageIfExists() throws SQLException {
    snowflakeStagingSqlOperations.dropStageIfExists(db, STAGE_NAME);
    String query = String.format("DROP STAGE IF EXISTS %s;", STAGE_NAME);
    verify(db, times(1)).execute(query);
  }

  @Test
  void cleanUpStage() throws SQLException {
    String path = "path";
    snowflakeStagingSqlOperations.cleanUpStage(db, path);
    String query = String.format("REMOVE @%s;", path);
    verify(db, times(1)).execute(query);
  }
}