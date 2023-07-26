/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks;

import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_JDBC_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_JDBC_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.databricks.utils.DatabricksConstants;
import io.airbyte.integrations.source.databricks.utils.DatabricksDatabaseUtil;
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
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;
import org.apache.commons.lang3.RandomStringUtils;

public class DatabricksSourceAcceptanceTest extends SourceAcceptanceTest {

  private JsonNode config;
  protected JdbcDatabase database;
  protected DataSource dataSource;

  protected static final String SCHEMA_NAME = "source_integration_test_"
      + RandomStringUtils.randomAlphanumeric(4).toLowerCase();
  private static final String STREAM_NAME1 = "id_and_name1";
  private static final String STREAM_NAME2 = "id_and_name2";

  JsonNode getStaticConfig() {
    return Jsons
        .deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-databricks:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                    STREAM_NAME1, SCHEMA_NAME,
                    Field.of("id", JsonSchemaType.NUMBER),
                    Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(CatalogHelpers.createAirbyteStream(
                    STREAM_NAME2, SCHEMA_NAME,
                    Field.of("id", JsonSchemaType.NUMBER),
                    Field.of("name", JsonSchemaType.STRING))
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
    JsonNode staticConfig = getStaticConfig();
    config = staticConfig;

    dataSource = DatabricksSourceTestUtil.createDataSource(staticConfig);
    database = new DefaultJdbcDatabase(dataSource, new DatabricksSourceOperations());
    final String createSchemaQuery = String.format("CREATE SCHEMA IF NOT EXISTS %s", SCHEMA_NAME);
    final String createTableQuery1 = String
        .format("CREATE OR REPLACE TABLE %s.%s (id INTEGER, name VARCHAR(200))", SCHEMA_NAME,
            STREAM_NAME1);
    final String createTableQuery2 = String
        .format("CREATE OR REPLACE TABLE %s.%s (id INTEGER, name VARCHAR(200))", SCHEMA_NAME,
            STREAM_NAME2);
    final String insertIntoTableQuery1 = String
        .format("INSERT INTO %s.%s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
            SCHEMA_NAME, STREAM_NAME1);
    final String insertIntoTableQuery2 = String
        .format("INSERT INTO %s.%s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
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
      final String dropStream1Query = String
          .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME, STREAM_NAME1);
      database.execute(dropStream1Query);
      final String dropStream2Query = String
          .format("DROP TABLE IF EXISTS %s.%s", SCHEMA_NAME, STREAM_NAME2);
      database.execute(dropStream2Query);
      final String dropSchemaQuery = String
          .format("DROP SCHEMA IF EXISTS %s", SCHEMA_NAME);
      database.execute(dropSchemaQuery);
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

}
