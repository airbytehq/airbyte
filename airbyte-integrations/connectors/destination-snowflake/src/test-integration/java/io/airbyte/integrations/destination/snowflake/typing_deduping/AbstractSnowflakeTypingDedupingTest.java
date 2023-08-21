package io.airbyte.integrations.destination.snowflake.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts;
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabase;
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils;
import java.nio.file.Path;
import java.util.List;
import javax.sql.DataSource;

public abstract class AbstractSnowflakeTypingDedupingTest extends BaseTypingDedupingTest {

  private String databaseName;
  private JdbcDatabase database;
  private DataSource dataSource;

  protected abstract String getConfigPath();

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode generateConfig() {
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(getConfigPath())));
    ((ObjectNode)config).put("schema", "typing_deduping_default_schema" + getUniqueSuffix());
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS);
    database = SnowflakeDatabase.getDatabase(dataSource);
    return config;
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    final String tableName = StreamId.concatenateRawTableName(streamNamespace, streamName);
    final String schema = getRawSchema();
    return SnowflakeTestUtils.dumpRawTable(
        database,
        // Explicitly wrap in quotes to prevent snowflake from upcasing
        '"'+ schema + "\".\"" + tableName + '"');
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    return SnowflakeTestUtils.dumpFinalTable(database, databaseName, streamNamespace, streamName);
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    database.execute(
        String.format(
          """
              DROP TABLE IF EXISTS "%s"."%s";
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
    return JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
  }

  private String getDefaultSchema() {
    return getConfig().get("schema").asText();
  }
}
