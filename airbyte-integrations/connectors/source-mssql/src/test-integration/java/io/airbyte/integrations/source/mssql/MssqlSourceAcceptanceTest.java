/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.Assert.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
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
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

public class MssqlSourceAcceptanceTest extends SourceAcceptanceTest {

  protected static final String SCHEMA_NAME = "dbo";
  protected static final String STREAM_NAME = "id_and_name";
  protected static final String STREAM_NAME2 = "starships";

  protected MsSQLTestDatabase testdb;

  @Override
  protected FeatureFlags featureFlags() {
    return FeatureFlagsWrapper.overridingUseStreamCapableState(super.featureFlags(), true);
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws SQLException {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022)
        .with("CREATE TABLE id_and_name (id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));")
        .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME2)
        .with("INSERT INTO id_and_name (id, name, born) VALUES " +
            "(1, 'picard', '2124-03-04T01:01:01Z'), " +
            "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
            "(3, 'vash', '2124-03-04T01:01:01Z');")
        .with("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato'), (4, 'Argo');", SCHEMA_NAME, STREAM_NAME2);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
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
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
        .build();
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        STREAM_NAME,
        SCHEMA_NAME,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("name", JsonSchemaType.STRING),
        Field.of("born", JsonSchemaType.STRING));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Test
  protected void testAddNewStreamToExistingSync() throws Exception {
    final List<ConfiguredAirbyteStream> configuredAirbyteStreams =
        Lists.newArrayList(CatalogHelpers.createConfiguredAirbyteStream(STREAM_NAME,
            SCHEMA_NAME,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("id")),
            CatalogHelpers.createConfiguredAirbyteStream(STREAM_NAME2,
                SCHEMA_NAME,
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withSyncMode(SyncMode.INCREMENTAL)
                .withCursorField(List.of("id")));
    final ConfiguredAirbyteCatalog configuredCatalogWithOneStream =
        new ConfiguredAirbyteCatalog().withStreams(List.of(configuredAirbyteStreams.get(0)));

    // Start a sync with one stream
    final List<AirbyteMessage> messages = runRead(withSourceDefinedCursors(configuredCatalogWithOneStream));
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);
    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);
    final AirbyteStreamState streamState = lastStateMessage.getStream();

    assertEquals(3, recordMessages.size());
    assertEquals(1, stateMessages.size());
    assertEquals(STREAM_NAME, streamState.getStreamDescriptor().getName());
    assertEquals(SCHEMA_NAME, streamState.getStreamDescriptor().getNamespace());

    final ConfiguredAirbyteCatalog configuredCatalogWithTwoStreams =
        new ConfiguredAirbyteCatalog().withStreams(configuredAirbyteStreams);

    // Start another sync with a newly added stream
    final List<AirbyteMessage> messages2 = runRead(configuredCatalogWithTwoStreams, Jsons.jsonNode(List.of(lastStateMessage)));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(4, recordMessages2.size());
    assertEquals(2, stateMessages2.size());

    assertEquals(2, stateMessages2.size());
    assertEquals(STREAM_NAME, stateMessages2.get(0).getStream().getStreamDescriptor().getName());
    assertEquals(SCHEMA_NAME, stateMessages2.get(0).getStream().getStreamDescriptor().getNamespace());
    assertEquals(STREAM_NAME2, stateMessages2.get(1).getStream().getStreamDescriptor().getName());
    assertEquals(SCHEMA_NAME, stateMessages2.get(1).getStream().getStreamDescriptor().getNamespace());
  }

  private List<AirbyteStateMessage> filterStateMessages(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == AirbyteMessage.Type.STATE).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

}
