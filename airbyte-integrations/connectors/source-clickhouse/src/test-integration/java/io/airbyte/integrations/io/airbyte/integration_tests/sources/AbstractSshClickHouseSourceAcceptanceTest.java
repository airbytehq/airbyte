/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import org.testcontainers.containers.ClickHouseContainer;

public abstract class AbstractSshClickHouseSourceAcceptanceTest extends SourceAcceptanceTest {

  private ClickHouseContainer db;
  private final SshBastionContainer bastion = new SshBastionContainer();
  private static JsonNode config;
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String SCHEMA_NAME = "default";

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
                String.format("%s.%s", config.get("database").asText(), STREAM_NAME),
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", config.get("database").asText(), STREAM_NAME2),
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    startTestContainers();
    config = bastion.getTunnelConfig(getTunnelMethod(), bastion.getBasicDbConfigBuider(db, "default"));
    populateDatabaseTestData();

  }

  private void startTestContainers() {
    bastion.initAndStartBastion();
    initAndStartJdbcContainer();
  }

  private void initAndStartJdbcContainer() {
    db = (ClickHouseContainer) new ClickHouseContainer("yandex/clickhouse-server:21.8.8.29-alpine").withNetwork(bastion.getNetWork());
    db.start();
  }

  private static void populateDatabaseTestData() throws Exception {
    final JdbcDatabase database = Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:clickhouse://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        ClickHouseSource.DRIVER_CLASS);

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

    database.close();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bastion.stopAndCloseContainers(db);
  }

}
