/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
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

  protected static final String SLOT_NAME_BASE = "debezium_slot";
  protected static final String NAMESPACE = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  protected static final String PUBLICATION = "publication";
  protected static final int INITIAL_WAITING_SECONDS = 5;

  protected PostgreSQLContainer<?> container;
  protected JsonNode config;

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
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.SCHEMAS_KEY, List.of(NAMESPACE))
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put("replication_method", replicationMethod)
        .put(JdbcUtils.SSL_KEY, false)
        .put("is_test", true)
        .build());

    try (final DSLContext dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES)) {
      final Database database = new Database(dslContext);

      /**
       * cdc expects the INCREMENTAL tables to contain primary key checkout
       * {@link io.airbyte.integrations.source.postgres.PostgresSource#removeIncrementalWithoutPk(AirbyteStream)}
       */
      database.query(ctx -> {
        ctx.execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
        ctx.execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
        ctx.execute("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
        ctx.execute("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
        ctx.execute("SELECT pg_create_logical_replication_slot('" + SLOT_NAME_BASE + "', 'pgoutput');");
        ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR ALL TABLES;");
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
                Field.of("id", JsonSchemaType.INTEGER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                NAMESPACE,
                Field.of("id", JsonSchemaType.INTEGER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalogWithPartialColumns() {
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
                Field.of("id", JsonSchemaType.INTEGER)
            /* no name field */)
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("name"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                NAMESPACE,
                /* no id field */
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Test
  public void testFullRefreshReadSelectedColumns() throws Exception {
    final ConfiguredAirbyteCatalog catalog = withFullRefreshSyncModes(getConfiguredCatalogWithPartialColumns());
    final List<AirbyteMessage> allMessages = runRead(catalog);

    final List<AirbyteRecordMessage> records = filterRecords(allMessages);
    assertFalse(records.isEmpty(), "Expected a full refresh sync to produce records");
    verifyFieldNotExist(records, STREAM_NAME, "name");
    verifyFieldNotExist(records, STREAM_NAME2, "id");
  }

  @Test
  public void testIncrementalReadSelectedColumns() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalogWithPartialColumns();
    final List<AirbyteMessage> allMessages = runRead(catalog);

    final List<AirbyteRecordMessage> records = filterRecords(allMessages);
    assertFalse(records.isEmpty(), "Expected a incremental sync to produce records");
    verifyFieldNotExist(records, STREAM_NAME, "name");
    verifyFieldNotExist(records, STREAM_NAME2, "id");
  }

  private void verifyFieldNotExist(final List<AirbyteRecordMessage> records, final String stream, final String field) {
    assertTrue(records.stream()
        .filter(r -> {
          return r.getStream().equals(stream)
              && r.getData().get(field) != null;
        })
        .collect(Collectors.toList())
        .isEmpty(), "Records contain unselected columns [%s:%s]".formatted(stream, field));
  }

}
