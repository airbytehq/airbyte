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
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts;
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabase;
import io.airbyte.integrations.destination.snowflake.SnowflakeTestSourceOperations;
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils;
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
    String schema = getRawSchema();
    return SnowflakeTestUtils.dumpRawTable(
        database,
        // Explicitly wrap in quotes to prevent snowflake from upcasing
        '"'+ schema + "\".\"" + tableName + '"');
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, String streamName) throws Exception {
    return Collections.emptyList();
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, String streamName) throws Exception {
    // TODO create test class for raw schema override
    database.execute(
        String.format(
          """
              DROP TABLE IF EXISTS %s.%s;
              DROP SCHEMA IF EXISTS "%s" CASCADE
              """,
            getRawSchema(),
            StreamId.concatenateRawTableName(streamNamespace, streamName),
            streamNamespace));
  }

  @Override
  protected void globalTeardown() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  /**
   * Subclasses using a config with a nonstandard raw table schema should override this method.
   */
  protected String getRawSchema() {
    return CatalogParser.DEFAULT_RAW_TABLE_NAMESPACE;
  }
}
