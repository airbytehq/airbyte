/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.snowflake.SnowflakeSource;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import javax.sql.DataSource;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

public class SnowflakeSourceAcceptanceTest extends SourceAcceptanceTest {

  protected static final String SCHEMA_NAME = "SOURCE_INTEGRATION_TEST_"
      + RandomStringUtils.randomAlphanumeric(4).toUpperCase();
  private static final String STREAM_NAME1 = "ID_AND_NAME1";
  private static final String STREAM_NAME2 = "ID_AND_NAME2";

  // config which refers to the schema that the test is being run in.
  protected JsonNode config;
  protected JdbcDatabase database;
  protected DataSource dataSource;

  @Override
  protected String getImageName() {
    return "airbyte/source-snowflake:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  JsonNode getStaticConfig() {
    return Jsons
        .deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("ID"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME1, SCHEMA_NAME,
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, SCHEMA_NAME,
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  // for each test we create a new schema in the database. run the test in there and then remove it.
  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    dataSource = createDataSource();
    database = new DefaultJdbcDatabase(dataSource, JdbcUtils.getDefaultSourceOperations());
    final String createSchemaQuery = String.format("CREATE SCHEMA IF NOT EXISTS %s", SCHEMA_NAME);
    final String createTableQuery1 = String
        .format("CREATE OR REPLACE TABLE %s.%s (ID INTEGER, NAME VARCHAR(200))", SCHEMA_NAME,
            STREAM_NAME1);
    final String createTableQuery2 = String
        .format("CREATE OR REPLACE TABLE %s.%s (ID INTEGER, NAME VARCHAR(200))", SCHEMA_NAME,
            STREAM_NAME2);
    final String insertIntoTableQuery1 = String
        .format("INSERT INTO %s.%s (ID, NAME) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
            SCHEMA_NAME, STREAM_NAME1);
    final String insertIntoTableQuery2 = String
        .format("INSERT INTO %s.%s (ID, NAME) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
            SCHEMA_NAME, STREAM_NAME2);

    database.execute(createSchemaQuery);
    database.execute(createTableQuery1);
    database.execute(createTableQuery2);
    database.execute(insertIntoTableQuery1);
    database.execute(insertIntoTableQuery2);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    try {
      final String dropSchemaQuery = String
          .format("DROP SCHEMA IF EXISTS %s", SCHEMA_NAME);
      database.execute(dropSchemaQuery);
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

  protected DataSource createDataSource() {
    config = Jsons.clone(getStaticConfig());
    return DataSourceFactory.create(
        config.get("credentials").get(JdbcUtils.USERNAME_KEY).asText(),
        config.get("credentials").get(JdbcUtils.PASSWORD_KEY).asText(),
        SnowflakeSource.DRIVER_CLASS,
        String.format(DatabaseDriver.SNOWFLAKE.getUrlFormatString(), config.get(JdbcUtils.HOST_KEY).asText()),
        Map.of("role", config.get("role").asText(),
            "warehouse", config.get("warehouse").asText(),
            JdbcUtils.DATABASE_KEY, config.get(JdbcUtils.DATABASE_KEY).asText()));
  }

  @Test
  public void testBackwardCompatibilityAfterAddingOAuth() throws Exception {
    final JsonNode deprecatedStyleConfig = Jsons.clone(config);
    final JsonNode password = deprecatedStyleConfig.get("credentials").get(JdbcUtils.PASSWORD_KEY);
    final JsonNode username = deprecatedStyleConfig.get("credentials").get(JdbcUtils.USERNAME_KEY);

    ((ObjectNode) deprecatedStyleConfig).remove("credentials");
    ((ObjectNode) deprecatedStyleConfig).set(JdbcUtils.PASSWORD_KEY, password);
    ((ObjectNode) deprecatedStyleConfig).set(JdbcUtils.USERNAME_KEY, username);

    assertEquals("SUCCEEDED", runCheckAndGetStatusAsString(deprecatedStyleConfig).toUpperCase());
  }

}
