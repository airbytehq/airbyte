/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.legacy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.ssh.SshBastionContainer;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.base.ssh.SshTunnel;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.HashMap;
import java.util.List;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractSshMssqlSourceAcceptanceTest extends SourceAcceptanceTest {

  static private final Logger LOGGER = LoggerFactory.getLogger(AbstractSshMssqlSourceAcceptanceTest.class);

  private static final String SCHEMA_NAME = "dbo";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  private final SshBastionContainer bastion = new SshBastionContainer();
  private MsSQLTestDatabase testdb;

  @Override
  protected JsonNode getConfig() {
    try {
      return testdb.integrationTestConfigBuilder()
          .withoutSsl()
          .with("tunnel_method", bastion.getTunnelMethod(getTunnelMethod(), true))
          .build();
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    } catch (InterruptedException e) {
      throw new RuntimeException(e);
    }
  }

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
        (CheckedFunction<JsonNode, List<JsonNode>, Exception>) mangledConfig -> getDatabaseFromConfig(mangledConfig)
            .query(ctx -> {
              ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));");
              ctx.fetch("INSERT INTO id_and_name (id, name, born) VALUES " +
                  "(1, 'picard', '2124-03-04T01:01:01Z'), " +
                  "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
                  "(3, 'vash', '2124-03-04T01:01:01Z');");
              return null;
            }));
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    return new Database(
        DSLContextFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.MSSQLSERVER.getDriverClassName(),
            String.format(DatabaseDriver.MSSQLSERVER.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText()) + ";encrypt=false;trustServerCertificate=true",
            SQLDialect.DEFAULT));
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022);
    LOGGER.info("starting bastion");
    bastion.initAndStartBastion(testdb.getContainer().getNetwork());
    LOGGER.info("bastion started");
    populateDatabaseTestData();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndClose();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.getSpecAndInjectSsh();
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
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
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

}
