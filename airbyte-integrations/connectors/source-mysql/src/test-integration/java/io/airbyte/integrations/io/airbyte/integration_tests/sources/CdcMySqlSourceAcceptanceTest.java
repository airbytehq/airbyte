/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.protocol.models.v0.SyncMode.FULL_REFRESH;
import static io.airbyte.protocol.models.v0.SyncMode.INCREMENTAL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.Assert;
import org.junit.jupiter.api.Test;

public class CdcMySqlSourceAcceptanceTest extends SourceAcceptanceTest {

  protected static final String STREAM_NAME = "id_and_name";
  protected static final String STREAM_NAME2 = "starships";
  protected static final String STREAM_NAME3 = "stream3";

  protected MySQLTestDatabase testdb;

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.getSpecAndInjectSsh();
  }

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withCdcReplication()
        .withoutSsl()
        .build();
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME, testdb.getDatabaseName(),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, testdb.getDatabaseName(),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return null;
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {
    testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8, getContainerModifiers())
        .withCdcPermissions()
        .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
        .with("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');")
        .with("CREATE TABLE starships(id INTEGER, name VARCHAR(200));")
        .with("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');")
        .with("CREATE TABLE %s (id INTEGER PRIMARY KEY, name VARCHAR(200), userid INTEGER DEFAULT NULL);", STREAM_NAME3)
        .with("INSERT INTO %s (id, name) VALUES (4,'voyager');", STREAM_NAME3);
  }

  protected ContainerModifier[] getContainerModifiers() {
    return ArrayUtils.toArray();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Test
  public void testIncrementalSyncShouldNotFailIfBinlogIsDeleted() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = withSourceDefinedCursors(getConfiguredCatalog());
    // only sync incremental streams
    configuredCatalog.setStreams(
        configuredCatalog.getStreams().stream().filter(s -> s.getSyncMode() == INCREMENTAL).collect(Collectors.toList()));

    final List<AirbyteMessage> airbyteMessages = runRead(configuredCatalog, getState());
    final List<AirbyteRecordMessage> recordMessages = filterRecords(airbyteMessages);
    final List<AirbyteStateMessage> stateMessages = airbyteMessages
        .stream()
        .filter(m -> m.getType() == AirbyteMessage.Type.STATE)
        .map(AirbyteMessage::getState)
        .collect(Collectors.toList());
    assertFalse(recordMessages.isEmpty(), "Expected the first incremental sync to produce records");
    assertFalse(stateMessages.isEmpty(), "Expected incremental sync to produce STATE messages");

    // when we run incremental sync again there should be no new records. Run a sync with the latest
    // state message and assert no records were emitted.
    final JsonNode latestState = Jsons.jsonNode(List.of(Iterables.getLast(stateMessages)));
    // RESET MASTER removes all binary log files that are listed in the index file,
    // leaving only a single, empty binary log file with a numeric suffix of .000001
    testdb.with("RESET MASTER;");

    assertEquals(6, filterRecords(runRead(configuredCatalog, latestState)).size());
  }

  @Test
  public void testIncrementalReadSelectedColumns() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalogWithPartialColumns();
    final List<AirbyteMessage> allMessages = runRead(catalog);

    final List<AirbyteRecordMessage> records = filterRecords(allMessages);
    assertFalse(records.isEmpty(), "Expected a incremental sync to produce records");
    verifyFieldNotExist(records, STREAM_NAME, "name");
    verifyFieldNotExist(records, STREAM_NAME2, "name");
  }

  private ConfiguredAirbyteCatalog getConfiguredCatalogWithPartialColumns() {
    // We cannot strip the primary key field as that is required for a successful CDC sync
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME, testdb.getDatabaseName(),
                Field.of("id", JsonSchemaType.NUMBER)
            /* no name field */)
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, testdb.getDatabaseName(),
                /* no name field */
                Field.of("id", JsonSchemaType.NUMBER))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, INCREMENTAL)))));
  }

  private void verifyFieldNotExist(final List<AirbyteRecordMessage> records, final String stream, final String field) {
    assertTrue(records.stream().noneMatch(r -> r.getStream().equals(stream) && r.getData().get(field) != null),
        "Records contain unselected columns [%s:%s]".formatted(stream, field));
  }

  @Test
  protected void testNullValueConversion() throws Exception {
    final List<ConfiguredAirbyteStream> configuredAirbyteStreams =
        Lists.newArrayList(new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(STREAM_NAME3,
                testdb.getDatabaseName(),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING),
                Field.of("userid", JsonSchemaType.NUMBER))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(Lists.newArrayList(FULL_REFRESH, INCREMENTAL))));

    final ConfiguredAirbyteCatalog configuredCatalogWithOneStream =
        new ConfiguredAirbyteCatalog().withStreams(List.of(configuredAirbyteStreams.get(0)));

    final List<AirbyteMessage> airbyteMessages = runRead(configuredCatalogWithOneStream, getState());
    final List<AirbyteRecordMessage> recordMessages = filterRecords(airbyteMessages);
    final List<AirbyteStateMessage> stateMessages = airbyteMessages
        .stream()
        .filter(m -> m.getType() == AirbyteMessage.Type.STATE)
        .map(AirbyteMessage::getState)
        .collect(Collectors.toList());
    Assert.assertEquals(recordMessages.size(), 1);
    assertFalse(stateMessages.isEmpty(), "Reason");
    ObjectMapper mapper = new ObjectMapper();

    assertEquals(cdcFieldsOmitted(recordMessages.get(0).getData()),
        mapper.readTree("{\"id\":4, \"name\":\"voyager\", \"userid\":null}"));

    // when we run incremental sync again there should be no new records. Run a sync with the latest
    // state message and assert no records were emitted.
    JsonNode latestState = extractLatestState(stateMessages);

    testdb.getDatabase().query(c -> {
      return c.query("INSERT INTO %s.%s (id, name) VALUES (5,'deep space nine');".formatted(testdb.getDatabaseName(), STREAM_NAME3));
    }).execute();

    assert Objects.nonNull(latestState);
    final List<AirbyteRecordMessage> secondSyncRecords = filterRecords(runRead(configuredCatalogWithOneStream, latestState));
    assertFalse(
        secondSyncRecords.isEmpty(),
        "Expected the second incremental sync to produce records.");
    assertEquals(cdcFieldsOmitted(secondSyncRecords.get(0).getData()),
        mapper.readTree("{\"id\":5, \"name\":\"deep space nine\", \"userid\":null}"));

  }

  private JsonNode cdcFieldsOmitted(final JsonNode node) {
    ObjectMapper mapper = new ObjectMapper();
    ObjectNode object = mapper.createObjectNode();
    node.fieldNames().forEachRemaining(name -> {
      if (!name.toLowerCase().startsWith("_ab_cdc_")) {
        object.put(name, node.get(name));
      }

    });
    return object;
  }

}
