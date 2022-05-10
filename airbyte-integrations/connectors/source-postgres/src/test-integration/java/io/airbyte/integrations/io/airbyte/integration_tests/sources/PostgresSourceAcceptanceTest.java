/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.util.HashMap;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "public.id_and_name";
  private static final String STREAM_NAME2 = "public.starships";
  private static final String STREAM_NAME_MATERIALIZED_VIEW = "public.testview";

  private PostgreSQLContainer<?> container;
  private JsonNode config;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("schemas", Jsons.jsonNode(List.of("public")))
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("ssl", false)
        .put("replication_method", replicationMethod)
        .build());

    try (final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()), SQLDialect.POSTGRES)) {
      final Database database = new Database(dslContext);

      database.query(ctx -> {
        ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
        ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
        ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
        ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
        ctx.fetch("CREATE MATERIALIZED VIEW testview AS select * from id_and_name where id = '2';");
        return null;
      });
    }
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
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME_MATERIALIZED_VIEW,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
