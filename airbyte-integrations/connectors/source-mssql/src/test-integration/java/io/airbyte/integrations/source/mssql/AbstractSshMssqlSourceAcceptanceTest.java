/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.base.ssh.SshTunnel;
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
import java.util.HashMap;
import java.util.Objects;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.containers.Network;

public abstract class AbstractSshMssqlSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "dbo.id_and_name";
  private static final String STREAM_NAME2 = "dbo.starships";
  private static final Network network = Network.newNetwork();
  private static JsonNode config;
  private String dbName;
  private MSSQLServerContainer<?> db;
  private final SshBastionContainer bastion = new SshBastionContainer();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    startTestContainers();
    config = bastion.getTunnelConfig(getTunnelMethod(), getMSSQLDbConfigBuilder(db));
    populateDatabaseTestData();
  }

  public ImmutableMap.Builder<Object, Object> getMSSQLDbConfigBuilder(final JdbcDatabaseContainer<?> db) {
    dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();
    return ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, Objects.requireNonNull(db.getContainerInfo().getNetworkSettings()
            .getNetworks()
            .get(((Network.NetworkImpl) network).getName())
            .getIpAddress()))
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.PORT_KEY, db.getExposedPorts().get(0))
        .put(JdbcUtils.DATABASE_KEY, dbName);
  }

  private static Database getDatabaseFromConfig(final JsonNode config) {
    final DSLContext dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d;",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()),
        null);
    return new Database(dslContext);
  }

  private void startTestContainers() {
    bastion.initAndStartBastion(network);
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2017-latest")
        .withNetwork(network)
        .acceptLicense();
    db.start();
  }

  private void populateDatabaseTestData() throws Exception {
    SshTunnel.sshWrap(
        getConfig(),
        JdbcUtils.HOST_LIST_KEY,
        JdbcUtils.PORT_LIST_KEY,
        mangledConfig -> {
          getDatabaseFromConfig(mangledConfig).query(ctx -> {
            ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
            ctx.fetch(String.format("ALTER DATABASE %s SET AUTO_CLOSE OFF WITH NO_WAIT;", dbName));
            ctx.fetch(String.format("USE %s;", dbName));
            ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));");
            ctx.fetch(
                "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
            return null;
          });
        });
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
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
                STREAM_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
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
