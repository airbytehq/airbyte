package io.airbyte.integrations.destination.snowflake.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts;
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabase;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class SnowflakeSqlGeneratorIntegrationTest extends BaseSqlGeneratorIntegrationTest<SnowflakeTableDefinition> {

  private static String databaseName;
  private static JdbcDatabase database;
  private static DataSource dataSource;

  @BeforeAll
  public static void setupSnowflake() {
    JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/1s1t_internal_staging_config.json")));
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS);
    database = SnowflakeDatabase.getDatabase(dataSource);
  }

  @AfterAll
  public static void teardownSnowflake() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  @Override
  protected SnowflakeSqlGenerator getSqlGenerator() {
    return new SnowflakeSqlGenerator();
  }

  @Override
  protected SnowflakeDestinationHandler getDestinationHandler() {
    return new SnowflakeDestinationHandler(databaseName, database);
  }

  @Override
  protected void createNamespace(String namespace) throws SQLException {
    database.execute("CREATE SCHEMA " + namespace);
  }

  @Override
  protected void createRawTable(StreamId streamId) throws Exception {
    database.execute(new StringSubstitutor(Map.of(
        "raw_table_id", streamId.rawTableId(SnowflakeSqlGenerator.QUOTE))).replace(
        """
            CREATE TABLE ${raw_table_id} (
              _airbyte_raw_id VARCHAR NOT NULL,
              _airbyte_data VARIANT NOT NULL,
              _airbyte_extracted_at TIMESTAMP_TZ NOT NULL,
              _airbyte_loaded_at TIMESTAMP_TZ
            )
            """));
  }

  @Override
  protected void createFinalTable(boolean includeCdcDeletedAt, StreamId streamId, String suffix) throws Exception {
    String cdcDeletedAt = includeCdcDeletedAt ? "`_ab_cdc_deleted_at` TIMESTAMP," : "";
    database.execute(new StringSubstitutor(Map.of(
            "final_table_id", streamId.finalTableId(SnowflakeSqlGenerator.QUOTE, suffix),
            "cdc_deleted_at", cdcDeletedAt)).replace(
            """
                CREATE TABLE ${final_table_id} (
                  _airbyte_raw_id VARCHAR NOT NULL,
                  _airbyte_extracted_at TIMESTAMP_TZ NOT NULL,
                  _airbyte_meta VARIANT NOT NULL,
                  `id1` INTEGER,
                  `id2` INTEGER,
                  `updated_at` TIMESTAMP_TZ,
                  ${cdc_deleted_at}
                  `struct` OBJECT,
                  `array` ARRAY,
                  `string` VARCHAR,
                  `number` NUMBER,
                  `integer` INTEGER,
                  `boolean` BOOLEAN,
                  `timestamp_with_timezone` TIMESTAMP_TZ,
                  `timestamp_without_timezone` TIMESTAMP_NTZ,
                  `time_with_timezone` VARCHAR,
                  `time_without_timezone` TIME,
                  `date` DATE,
                  `unknown` VARIANT
                )
                """));
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(StreamId streamId) throws Exception {
    return null;
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception {
    return null;
  }

  @Override
  protected void teardownNamespace(String namespace) throws SQLException {
    database.execute("DROP SCHEMA IF EXISTS " + namespace);
  }

  @Override
  @Test
  public void testCreateTableIncremental() throws Exception {

  }

  @Override
  protected void insertFinalTableRecords(boolean includeCdcDeletedAt, StreamId streamId, String suffix, List<JsonNode> records) throws Exception {

  }

  @Override
  protected void insertRawTableRecords(StreamId streamId, List<JsonNode> records) throws Exception {

  }
}
