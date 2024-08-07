/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.HashMap;
import java.util.List;
import org.jooq.SQLDialect;

public abstract class AbstractSshPostgresSourceAcceptanceTest extends AbstractPostgresSourceAcceptanceTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String SCHEMA_NAME = "public";

  private final SshBastionContainer bastion = new SshBastionContainer();
  private PostgresTestDatabase testdb;

  private void populateDatabaseTestData() throws Exception {
    final var outerConfig = testdb.integrationTestConfigBuilder()
        .withSchemas("public")
        .withoutSsl()
        .with("tunnel_method", bastion.getTunnelMethod(getTunnelMethod(), false))
        .build();
    SshTunnel.sshWrap(
        outerConfig,
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        (CheckedConsumer<JsonNode, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(ctx -> {
              ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
              ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
              ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
              ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
              return null;
            }));
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    return new Database(
        DSLContextFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.POSTGRESQL.getDriverClassName(),
            String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText()),
            SQLDialect.POSTGRES));
  }

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  // todo (cgardens) - dynamically create data by generating a database with a random name instead of
  // requiring data to already be in place.
  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_16, ContainerModifier.NETWORK);
    bastion.initAndStartBastion(testdb.getContainer().getNetwork());
    populateDatabaseTestData();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndClose();
  }

  @Override
  protected JsonNode getConfig() {
    try {
      return testdb.integrationTestConfigBuilder()
          .withSchemas("public")
          .withoutSsl()
          .with("tunnel_method", bastion.getTunnelMethod(getTunnelMethod(), true))
          .build();
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.INTEGER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.INTEGER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(List.of(List.of("id"))))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
