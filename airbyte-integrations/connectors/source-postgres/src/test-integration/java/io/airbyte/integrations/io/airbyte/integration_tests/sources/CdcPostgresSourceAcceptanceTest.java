/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.cdk.testutils.PostgresTestDatabase;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

// todo (cgardens) - Sanity check that when configured for CDC that postgres performs like any other
// incremental source. As we have more sources support CDC we will find a more reusable way of doing
// this, but for now this is a solid sanity check.
public class CdcPostgresSourceAcceptanceTest extends AbstractPostgresSourceAcceptanceTest {

  protected static final String NAMESPACE = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  protected static final int INITIAL_WAITING_SECONDS = 30;

  protected PostgresTestDatabase testdb;
  protected JsonNode config;
  protected String slotName;
  protected String publication;

  @Override
  protected FeatureFlags featureFlags() {
    return FeatureFlagsWrapper.overridingUseStreamCapableState(super.featureFlags(), true);
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = PostgresTestDatabase.make(getServerImageName(), "withConf");
    slotName = testdb.withSuffix("debezium_slot");
    publication = testdb.withSuffix("publication");
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", slotName)
        .put("publication", publication)
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .build());

    config = Jsons.jsonNode(testdb.makeConfigBuilder()
        .put(JdbcUtils.SCHEMAS_KEY, List.of(NAMESPACE))
        .put("replication_method", replicationMethod)
        .put(JdbcUtils.SSL_KEY, false)
        .put("is_test", true)
        .build());

    testdb.database.query(ctx -> {
      ctx.execute("CREATE TABLE id_and_name(id INTEGER  primary key, name VARCHAR(200));");
      ctx.execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      ctx.execute("CREATE TABLE starships(id INTEGER primary key, name VARCHAR(200));");
      ctx.execute("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
      ctx.execute("SELECT pg_create_logical_replication_slot('" + slotName + "', 'pgoutput');");
      ctx.execute("CREATE PUBLICATION " + publication + " FOR ALL TABLES;");
      return null;
    });
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    testdb.database.query(ctx -> {
      ctx.execute("SELECT pg_drop_replication_slot('" + slotName + "');");
      ctx.execute("DROP PUBLICATION " + publication + " CASCADE;");
      return null;
    });
    testdb.close();
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
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                NAMESPACE,
                Field.of("id", JsonSchemaType.INTEGER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                NAMESPACE,
                Field.of("id", JsonSchemaType.INTEGER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalogWithPartialColumns() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                NAMESPACE,
                Field.of("id", JsonSchemaType.INTEGER)
            /* no name field */)
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                NAMESPACE,
                /* no id field */
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
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

  protected String getServerImageName() {
    return "postgres:16-bullseye";
  }

}
