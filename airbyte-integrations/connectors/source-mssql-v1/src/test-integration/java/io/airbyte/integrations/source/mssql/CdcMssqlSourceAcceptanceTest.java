/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.protocol.models.v0.SyncMode.FULL_REFRESH;
import static io.airbyte.protocol.models.v0.SyncMode.INCREMENTAL;
import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.junit.Assert;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

@TestInstance(Lifecycle.PER_METHOD)
@Execution(ExecutionMode.CONCURRENT)
public class CdcMssqlSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String SCHEMA_NAME = "dbo";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String CDC_ROLE_NAME = "cdc_selector";
  private static final String STREAM_NAME3 = "stream3";

  private MsSQLTestDatabase testdb;

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql-v1:dev";
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
    return new ConfiguredAirbyteCatalog().withStreams(getConfiguredAirbyteStreams());
  }

  protected List<ConfiguredAirbyteStream> getConfiguredAirbyteStreams() {
    return Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSourceDefinedCursor(true)
                .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));
  }

  @Override
  protected JsonNode getState() {
    return null;
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022, ContainerModifier.AGENT);
    testdb
        .withWaitUntilAgentRunning()
        .withCdc()
        // create tables
        .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME)
        .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME2)
        .with("CREATE TABLE %s.%s (id INTEGER PRIMARY KEY, name VARCHAR(200), userid INTEGER DEFAULT NULL);", SCHEMA_NAME, STREAM_NAME3)
        // populate tables
        .with("INSERT INTO %s.%s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');", SCHEMA_NAME, STREAM_NAME)
        .with("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');", SCHEMA_NAME, STREAM_NAME2)
        .with("INSERT INTO %s.%s (id, name) VALUES (4,'voyager');", SCHEMA_NAME, STREAM_NAME3)
        // enable cdc on tables for designated role
        .withCdcForTable(SCHEMA_NAME, STREAM_NAME, CDC_ROLE_NAME)
        .withCdcForTable(SCHEMA_NAME, STREAM_NAME2, CDC_ROLE_NAME)
        .withCdcForTable(SCHEMA_NAME, STREAM_NAME3, CDC_ROLE_NAME)
        // revoke user permissions
        .with("REVOKE ALL FROM %s CASCADE;", testdb.getUserName())
        .with("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO %s;\"", testdb.getUserName())
        // grant user permissions
        .with("EXEC sp_addrolemember N'%s', N'%s';", "db_datareader", testdb.getUserName())
        .with("GRANT SELECT ON SCHEMA :: [cdc] TO %s", testdb.getUserName())
        .with("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, testdb.getUserName())
        .withWaitUntilMaxLsnAvailable();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

  @Test
  void testAddNewStreamToExistingSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalogWithOneStream =
        new ConfiguredAirbyteCatalog().withStreams(List.of(getConfiguredAirbyteStreams().get(0)));

    // Start a sync with one stream
    final List<AirbyteMessage> messages = runRead(configuredCatalogWithOneStream);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);
    final List<AirbyteStreamState> streamStates = stateMessages.get(0).getGlobal().getStreamStates();

    assertEquals(3, recordMessages.size());
    assertEquals(2, stateMessages.size());
    assertEquals(1, streamStates.size());
    assertEquals(STREAM_NAME, streamStates.get(0).getStreamDescriptor().getName());
    assertEquals(SCHEMA_NAME, streamStates.get(0).getStreamDescriptor().getNamespace());

    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);

    final ConfiguredAirbyteCatalog configuredCatalogWithTwoStreams = configuredCatalogWithOneStream.withStreams(getConfiguredAirbyteStreams());

    // Start another sync with a newly added stream
    final List<AirbyteMessage> messages2 = runRead(configuredCatalogWithTwoStreams, Jsons.jsonNode(List.of(lastStateMessage)));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(3, recordMessages2.size());
    assertEquals(2, stateMessages2.size());

    final AirbyteStateMessage lastStateMessage2 = Iterables.getLast(stateMessages2);
    final List<AirbyteStreamState> streamStates2 = lastStateMessage2.getGlobal().getStreamStates();

    assertEquals(2, streamStates2.size());

    assertEquals(STREAM_NAME, streamStates2.get(0).getStreamDescriptor().getName());
    assertEquals(SCHEMA_NAME, streamStates2.get(0).getStreamDescriptor().getNamespace());
    assertEquals(STREAM_NAME2, streamStates2.get(1).getStreamDescriptor().getName());
    assertEquals(SCHEMA_NAME, streamStates2.get(1).getStreamDescriptor().getNamespace());
  }

  private List<AirbyteStateMessage> filterStateMessages(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == AirbyteMessage.Type.STATE).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  @Test
  protected void testNullValueConversion() throws Exception {
    final List<ConfiguredAirbyteStream> configuredAirbyteStreams =
        Lists.newArrayList(new ConfiguredAirbyteStream()
            .withSyncMode(INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(STREAM_NAME3,
                SCHEMA_NAME,
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

    assertTrue(cdcFieldsOmitted(recordMessages.get(0).getData()).equals(
        mapper.readTree("{\"id\":4, \"name\":\"voyager\", \"userid\":null}")));

    // when we run incremental sync again there should be no new records. Run a sync with the latest
    // state message and assert no records were emitted.
    JsonNode latestState = extractLatestState(stateMessages);

    testdb.getDatabase().query(c -> c.query("INSERT INTO %s.%s (id, name) VALUES (5,'deep space nine')".formatted(SCHEMA_NAME, STREAM_NAME3)))
        .execute();

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
