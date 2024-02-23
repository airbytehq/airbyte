/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import org.junit.jupiter.api.Test;

public class PostgresSourceAcceptanceTest extends AbstractPostgresSourceAcceptanceTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String STREAM_NAME_MATERIALIZED_VIEW = "testview";
  private static final String SCHEMA_NAME = "public";
  public static final String LIMIT_PERMISSION_SCHEMA = "limit_perm_schema";
  static public final String LIMIT_PERMISSION_ROLE_PASSWORD = "test";

  private PostgresTestDatabase testdb;
  private JsonNode config;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = PostgresTestDatabase.in(getServerImage());
    config = getConfig(testdb.getUserName(), testdb.getPassword(), "public");
    testdb.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
      ctx.fetch("CREATE MATERIALIZED VIEW testview AS select * from id_and_name where id = '2';");
      return null;
    });
  }

  private String getLimitPermissionRoleName() {
    return testdb.withNamespace("limit_perm_role");
  }

  private JsonNode getConfig(final String username, final String password, String... schemas) {
    return testdb.configBuilder()
        .withResolvedHostAndPort()
        .withDatabase()
        .with(JdbcUtils.USERNAME_KEY, username)
        .with(JdbcUtils.PASSWORD_KEY, password)
        .withSchemas(schemas)
        .withoutSsl()
        .withStandardReplication()
        .build();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return getCommonConfigCatalog();
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Test
  public void testFullRefreshWithRevokingSchemaPermissions() throws Exception {
    prepareEnvForUserWithoutPermissions(testdb.getDatabase());

    config = getConfig(getLimitPermissionRoleName(), LIMIT_PERMISSION_ROLE_PASSWORD, LIMIT_PERMISSION_SCHEMA);
    final ConfiguredAirbyteCatalog configuredCatalog = getLimitPermissionConfiguredCatalog();

    final List<AirbyteRecordMessage> fullRefreshRecords = filterRecords(runRead(configuredCatalog));
    final String assertionMessage = "Expected records after full refresh sync for user with schema permission";
    assertFalse(fullRefreshRecords.isEmpty(), assertionMessage);

    revokeSchemaPermissions(testdb.getDatabase());

    final List<AirbyteRecordMessage> lessPermFullRefreshRecords = filterRecords(runRead(configuredCatalog));
    final String assertionMessageWithoutPermission = "Expected no records after full refresh sync for user without schema permission";
    assertTrue(lessPermFullRefreshRecords.isEmpty(), assertionMessageWithoutPermission);

  }

  @Test
  public void testDiscoverWithRevokingSchemaPermissions() throws Exception {
    prepareEnvForUserWithoutPermissions(testdb.getDatabase());
    revokeSchemaPermissions(testdb.getDatabase());
    config = getConfig(getLimitPermissionRoleName(), LIMIT_PERMISSION_ROLE_PASSWORD, LIMIT_PERMISSION_SCHEMA);

    runDiscover();
    final AirbyteCatalog lastPersistedCatalogSecond = getLastPersistedCatalog();
    final String assertionMessageWithoutPermission = "Expected no streams after discover for user without schema permissions";
    assertTrue(lastPersistedCatalogSecond.getStreams().isEmpty(), assertionMessageWithoutPermission);
  }

  private void revokeSchemaPermissions(final Database database) throws SQLException {
    database.query(ctx -> {
      ctx.fetch(String.format("REVOKE USAGE ON schema %s FROM %s;", LIMIT_PERMISSION_SCHEMA, getLimitPermissionRoleName()));
      return null;
    });
  }

  private void prepareEnvForUserWithoutPermissions(final Database database) throws SQLException {
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE ROLE %s WITH LOGIN PASSWORD '%s';", getLimitPermissionRoleName(), LIMIT_PERMISSION_ROLE_PASSWORD));
      ctx.fetch(String.format("CREATE SCHEMA %s;", LIMIT_PERMISSION_SCHEMA));
      ctx.fetch(String.format("GRANT CONNECT ON DATABASE %s TO %s;", testdb.getDatabaseName(), getLimitPermissionRoleName()));
      ctx.fetch(String.format("GRANT USAGE ON schema %s TO %s;", LIMIT_PERMISSION_SCHEMA, getLimitPermissionRoleName()));
      ctx.fetch(String.format("CREATE TABLE %s.id_and_name(id INTEGER, name VARCHAR(200));", LIMIT_PERMISSION_SCHEMA));
      ctx.fetch(String.format("INSERT INTO %s.id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');", LIMIT_PERMISSION_SCHEMA));
      ctx.fetch(String.format("GRANT SELECT ON table %s.id_and_name TO %s;", LIMIT_PERMISSION_SCHEMA, getLimitPermissionRoleName()));
      return null;
    });
  }

  private ConfiguredAirbyteCatalog getCommonConfigCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME_MATERIALIZED_VIEW, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of("id"))))));
  }

  private ConfiguredAirbyteCatalog getLimitPermissionConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                "id_and_name", LIMIT_PERMISSION_SCHEMA,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  protected BaseImage getServerImage() {
    return BaseImage.POSTGRES_16;
  }

}
