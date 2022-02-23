/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.ssh.SshHelpers;
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
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

// todo (cgardens) - Sanity check that when configured for CDC that postgres performs like any other
// incremental source. As we have more sources support CDC we will find a more reusable way of doing
// this, but for now this is a solid sanity check.
/**
 * None of the tests in this class use the cdc path (run the tests and search for `using CDC: false`
 * in logs). This is exact same as {@link PostgresSourceAcceptanceTest}
 */
public class CdcPostgresSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String SLOT_NAME_BASE = "debezium_slot";
  private static final String NAMESPACE = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String PUBLICATION = "publication";

  private PostgreSQLContainer<?> container;
  private JsonNode config;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"), "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();

    /**
     * The publication is not being set as part of the config and because of it
     * {@link io.airbyte.integrations.source.postgres.PostgresSource#isCdc(JsonNode)} returns false, as
     * a result no test in this class runs through the cdc path.
     */
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", SLOT_NAME_BASE)
        .put("publication", PUBLICATION)
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", replicationMethod)
        .put("ssl", false)
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver",
        SQLDialect.POSTGRES);
    /**
     * cdc expects the INCREMENTAL tables to contain primary key checkout
     * {@link io.airbyte.integrations.source.postgres.PostgresSource#removeIncrementalWithoutPk(AirbyteStream)}
     */
    database.query(ctx -> {
      ctx.execute("SELECT pg_create_logical_replication_slot('" + SLOT_NAME_BASE + "', 'pgoutput');");
      ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR ALL TABLES;");
      ctx.execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      ctx.execute("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
      ctx.execute("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
      return null;
    });

    database.close();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
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
    /**
     * This catalog config is incorrect for CDC replication. We specify
     * withCursorField(Lists.newArrayList("id")) but with CDC customers can't/shouldn't be able to
     * specify cursor field for INCREMENTAL tables Take a look at
     * {@link io.airbyte.integrations.source.postgres.PostgresSource#setIncrementalToSourceDefined(AirbyteStream)}
     * We should also specify the primary keys for INCREMENTAL tables checkout
     * {@link io.airbyte.integrations.source.postgres.PostgresSource#removeIncrementalWithoutPk(AirbyteStream)}
     */
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                NAMESPACE,
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                NAMESPACE,
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
