/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static java.time.temporal.ChronoUnit.SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
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
import java.time.Duration;
import java.util.HashMap;
import javax.sql.DataSource;
import org.testcontainers.containers.ClickHouseContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.wait.strategy.Wait;

public abstract class AbstractSshClickHouseSourceAcceptanceTest extends SourceAcceptanceTest {

  private ClickHouseContainer db;
  private final SshBastionContainer bastion = new SshBastionContainer();
  private static JsonNode config;
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String SCHEMA_NAME = "default";
  private static final Network network = Network.newNetwork();

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/source-clickhouse:dev";
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
                String.format("%s.%s", config.get(JdbcUtils.DATABASE_KEY).asText(), STREAM_NAME),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", config.get(JdbcUtils.DATABASE_KEY).asText(), STREAM_NAME2),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    startTestContainers();
    config = bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db, "default"), false);
    populateDatabaseTestData();

  }

  private void startTestContainers() {
    bastion.initAndStartBastion(network);
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = new ClickHouseContainer("clickhouse/clickhouse-server:22.5")
        .withNetwork(network)
        .waitingFor(Wait.forHttp("/ping").forPort(8123)
            .forStatusCode(200).withStartupTimeout(Duration.of(60, SECONDS)));
    db.start();
  }

  private static void populateDatabaseTestData() throws Exception {
    final DataSource dataSource = DataSourceFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        ClickHouseSource.DRIVER_CLASS,
        String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString(),
            ClickHouseSource.HTTP_PROTOCOL,
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()));

    try {
      final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

      final String table1 = JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME, STREAM_NAME);
      final String createTable1 =
          String.format("CREATE TABLE IF NOT EXISTS %s (id INTEGER, name VARCHAR(200)) ENGINE = TinyLog \n", table1);
      final String table2 = JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME, STREAM_NAME2);
      final String createTable2 =
          String.format("CREATE TABLE IF NOT EXISTS %s (id INTEGER, name VARCHAR(200)) ENGINE = TinyLog \n", table2);
      database.execute(connection -> {
        connection.createStatement().execute(createTable1);
        connection.createStatement().execute(createTable2);
      });

      final String insertTestData = String.format("INSERT INTO %s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');\n", table1);
      final String insertTestData2 = String.format("INSERT INTO %s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');\n", table2);
      database.execute(connection -> {
        connection.createStatement().execute(insertTestData);
        connection.createStatement().execute(insertTestData2);
      });
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

}
