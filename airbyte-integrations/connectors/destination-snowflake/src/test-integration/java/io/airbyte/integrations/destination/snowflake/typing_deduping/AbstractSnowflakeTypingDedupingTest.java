package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts;
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabase;
import io.airbyte.integrations.destination.snowflake.SnowflakeTestSourceOperations;
import java.nio.file.Path;
import java.sql.ResultSet;
import java.util.Collections;
import java.util.List;
import javax.sql.DataSource;

public abstract class AbstractSnowflakeTypingDedupingTest extends BaseTypingDedupingTest {

  private JdbcDatabase database;
  private DataSource dataSource;

  protected abstract String getConfigPath();

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode generateConfig() {
    JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(getConfigPath())));
    dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS);
    database = SnowflakeDatabase.getDatabase(dataSource);
    return config;
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws Exception {
    String tableName = StreamId.concatenateRawTableName(streamNamespace, streamName);
    String schema = "airbyte";
    // TODO this was copied from SnowflakeInsertDestinationAcceptanceTest, refactor it maybe
    return database.bufferedResultSetQuery(
        connection -> {
          try (final ResultSet tableInfo = connection.createStatement()
              .executeQuery(String.format("SHOW TABLES LIKE '%s' IN SCHEMA %s;", tableName, schema))) {
            assertTrue(tableInfo.next());
            // check that we're creating permanent tables. DBT defaults to transient tables, which have
            // `TRANSIENT` as the value for the `kind` column.
            assertEquals("TABLE", tableInfo.getString("kind"));
            connection.createStatement().execute("ALTER SESSION SET TIMEZONE = 'UTC';");
            return connection.createStatement()
                .executeQuery(String.format(
                    "SELECT %s,%s,%s,%s FROM %s.%s ORDER BY %s ASC;",
                    // Explicitly quote column names to prevent snowflake from upcasing them
                    '"' + JavaBaseConstants.COLUMN_NAME_AB_RAW_ID.toLowerCase() + '"',
                    '"' + JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT.toLowerCase() + '"',
                    '"' + JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT.toLowerCase() + '"',
                    '"' + JavaBaseConstants.COLUMN_NAME_DATA.toLowerCase() + '"',
                    schema,
                    tableName,
                    '"' + JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT.toLowerCase() + '"'));
          }
        },
        new SnowflakeTestSourceOperations()::rowToJson);
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, String streamName) throws Exception {
    return Collections.emptyList();
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, String streamName) throws Exception {
    database.execute(
        String.format(
          """
              DROP TABLE IF EXISTS airbyte.%s;
              DROP SCHEMA IF EXISTS %s CASCADE
              """,
            StreamId.concatenateRawTableName(streamNamespace, streamName),
            streamNamespace));
  }

  @Override
  protected void globalTeardown() throws Exception {
    DataSourceFactory.close(dataSource);
  }
}
