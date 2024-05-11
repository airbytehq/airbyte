/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
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

  protected PostgresTestDatabase testdb;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = PostgresTestDatabase.in(getServerImage(), ContainerModifier.CONF)
        .with("CREATE TABLE id_and_name(id INTEGER  primary key, name VARCHAR(200));")
        .with("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');")
        .with("CREATE TABLE starships(id INTEGER primary key, name VARCHAR(200));")
        .with("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');")
        .withReplicationSlot()
        .withPublicationForAllTables();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws SQLException {
    testdb.close();
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withSchemas(NAMESPACE)
        .withoutSsl()
        .withCdcReplication()
        .build();
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

  protected BaseImage getServerImage() {
    return BaseImage.POSTGRES_16;
  }

}
