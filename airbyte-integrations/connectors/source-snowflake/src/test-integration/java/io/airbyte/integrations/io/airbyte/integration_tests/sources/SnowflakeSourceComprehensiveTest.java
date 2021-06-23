package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.snowflake.SnowflakeSource;
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.nio.file.Path;
import org.jooq.SQLDialect;

public class SnowflakeSourceComprehensiveTest extends SourceComprehensiveTest {

  private static final String SCHEMA_NAME = "TEST";

  private JsonNode config;
  private Database database;

  @Override
  protected String getImageName() {
    return "airbyte/source-snowflake:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected Database setupDatabase() throws Exception {
    config = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));

    database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:snowflake://%s/",
            config.get("host").asText()),
        SnowflakeSource.DRIVER_CLASS,
        SQLDialect.DEFAULT,
        String.format("role=%s;warehouse=%s;database=%s",
            config.get("role").asText(),
            config.get("warehouse").asText(),
            config.get("database").asText()));

    final String createSchemaQuery = String.format("CREATE SCHEMA %s", SCHEMA_NAME);
    database.query(ctx -> ctx.fetch(createSchemaQuery));
    return database;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    final String dropSchemaQuery = String
        .format("DROP SCHEMA IF EXISTS %s", SCHEMA_NAME);
    database.query(ctx -> ctx.fetch(dropSchemaQuery));
    database.close();
  }

  @Override
  protected String getNameSpace() {
    return SCHEMA_NAME;
  }

  @Override
  protected String getIdColumnName() {
    return "ID";
  }

  @Override
  protected String getTestColumnName() {
    return "TEST_COLUMN";
  }

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("-99999999999999999999999999999999999999", "99999999999999999999999999999999999999")
            .addExpectedValues("-99999999999999999999999999999999999999", "99999999999999999999999999999999999999")
            .build());
  }
}
