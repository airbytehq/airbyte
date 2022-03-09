/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.db2.Db2Source;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.Db2Container;

public class Db2SourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String SCHEMA_NAME = "SOURCE_INTEGRATION_TEST";
  private static final String LESS_PERMITTED_USER = "db2inst2";
  private static final String USER_WITH_OUT_PERMISSIONS = "db2inst3";
  private static final String STREAM_NAME1 = "ID_AND_NAME1";
  private static final String STREAM_NAME2 = "ID_AND_NAME2";
  private static final String STREAM_NAME3 = "ID_AND_NAME3";
  public static final String PASSWORD = "password";

  private Db2Container db;
  private JsonNode config;
  private JdbcDatabase database;

  @Override
  protected String getImageName() {
    return "airbyte/source-db2:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  private JsonNode getConfig(String userName, String password) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("db", db.getDatabaseName())
        .put("username", userName)
        .put("password", password)
        .put("encryption", Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "unencrypted")
            .build()))
        .build());
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("ID"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", SCHEMA_NAME, STREAM_NAME1),
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", SCHEMA_NAME, STREAM_NAME2),
                Field.of("ID", JsonSchemaType.NUMBER),
                Field.of("NAME", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() throws Exception {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    db = new Db2Container("ibmcom/db2:11.5.5.0").acceptLicense();
    db.start();

    config = getConfig(db.getUsername(), db.getPassword());

    database = Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:db2://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("db").asText()),
        Db2Source.DRIVER_CLASS);

    final String createSchemaQuery = String.format("CREATE SCHEMA %s", SCHEMA_NAME);
    final String createTableQuery1 = String
        .format("CREATE TABLE %s.%s (ID INTEGER, NAME VARCHAR(200))", SCHEMA_NAME, STREAM_NAME1);
    final String createTableQuery2 = String
        .format("CREATE TABLE %s.%s (ID INTEGER, NAME VARCHAR(200))", SCHEMA_NAME, STREAM_NAME2);
    final String createTableQuery3 = String
        .format("CREATE TABLE %s.%s (ID INTEGER, NAME VARCHAR(200))", SCHEMA_NAME, STREAM_NAME3);
    final String insertIntoTableQuery1 = String
        .format("INSERT INTO %s.%s (ID, NAME) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
            SCHEMA_NAME, STREAM_NAME1);
    final String insertIntoTableQuery2 = String
        .format("INSERT INTO %s.%s (ID, NAME) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash')",
            SCHEMA_NAME, STREAM_NAME2);
    final String grantSelect1 = String
        .format("GRANT SELECT ON TABLE %s.%s TO %s",
            SCHEMA_NAME, STREAM_NAME1, LESS_PERMITTED_USER);
    final String grantSelect2 = String
        .format("GRANT SELECT ON TABLE %s.%s TO %s",
            SCHEMA_NAME, STREAM_NAME3, LESS_PERMITTED_USER);

    database.execute(createSchemaQuery);
    database.execute(createTableQuery1);
    database.execute(createTableQuery2);
    database.execute(createTableQuery3);
    database.execute(insertIntoTableQuery1);
    database.execute(insertIntoTableQuery2);
    database.execute(grantSelect1);
    database.execute(grantSelect2);

    database.close();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.close();
  }

  @Test
  public void testCheckPrivilegesForUserWithLessPerm() throws Exception {
    createUser(LESS_PERMITTED_USER);
    JsonNode config = getConfig(LESS_PERMITTED_USER, PASSWORD);

    final List<String> actualNamesWithPermission = getActualNamesWithPermission(config);
    List<String> expected = List.of(STREAM_NAME3, STREAM_NAME1);
    assertEquals(expected.size(), actualNamesWithPermission.size());
    assertEquals(expected, actualNamesWithPermission);
  }

  @Test
  public void testCheckPrivilegesForUserWithoutPerm() throws Exception {
    createUser(USER_WITH_OUT_PERMISSIONS);

    JsonNode config = getConfig(USER_WITH_OUT_PERMISSIONS, PASSWORD);

    final List<String> actualNamesWithPermission = getActualNamesWithPermission(config);
    List<String> expected = Collections.emptyList();
    assertEquals(0, actualNamesWithPermission.size());
    assertEquals(expected, actualNamesWithPermission);
  }

  private void createUser(String lessPermittedUser) throws IOException, InterruptedException {
    String encryptedPassword = db.execInContainer("openssl", "passwd", PASSWORD).getStdout().replaceAll("\n", "");
    db.execInContainer("useradd", lessPermittedUser, "-p", encryptedPassword);
  }

  private List<String> getActualNamesWithPermission(JsonNode config) throws Exception {
    AirbyteCatalog airbyteCatalog = new Db2Source().discover(config);
    return airbyteCatalog
        .getStreams()
        .stream()
        .map(AirbyteStream::getName)
        .toList();
  }

}
