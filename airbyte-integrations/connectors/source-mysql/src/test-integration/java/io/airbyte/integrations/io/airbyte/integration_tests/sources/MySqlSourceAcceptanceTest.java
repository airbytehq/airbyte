/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.protocol.models.v0.SyncMode.INCREMENTAL;
import static org.junit.Assert.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
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
import io.airbyte.protocol.models.v0.*;
import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.jupiter.api.Test;

public class MySqlSourceAcceptanceTest extends SourceAcceptanceTest {

  protected MySQLTestDatabase testdb;

  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "public.starships";

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8, getContainerModifiers())
        .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
        .with("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');")
        .with("CREATE TABLE starships(id INTEGER, name VARCHAR(200));")
        .with("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
  }

  protected ContainerModifier[] getContainerModifiers() {
    return ArrayUtils.toArray();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testdb.close();
  }

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
        .withStandardReplication()
        .withoutSsl()
        .build();
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME, testdb.getDatabaseName(),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2, testdb.getDatabaseName(),
                Field.of("id", JsonSchemaType.NUMBER),
                Field.of("name", JsonSchemaType.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Test
  protected void testNullValueConversion() throws Exception {
    final String STREAM_NAME3 = "stream3";
    testdb.getDatabase().query(c -> {
      return c.query("""
                     CREATE TABLE %s.%s (id INTEGER PRIMARY KEY, name VARCHAR(200), userid INTEGER DEFAULT NULL);
                     """.formatted(testdb.getDatabaseName(), STREAM_NAME3));
    }).execute();

    testdb.getDatabase().query(c -> {
      return c.query("""
                     INSERT INTO %s.%s (id, name) VALUES (4,'voyager');
                     """.formatted(testdb.getDatabaseName(), STREAM_NAME3));
    }).execute();

    final List<ConfiguredAirbyteStream> configuredAirbyteStreams =
        Lists.newArrayList(CatalogHelpers.createConfiguredAirbyteStream(STREAM_NAME3,
            testdb.getDatabaseName(),
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING),
            Field.of("userid", JsonSchemaType.NUMBER))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withSyncMode(INCREMENTAL)
            .withCursorField(List.of("id")));
    final ConfiguredAirbyteCatalog configuredCatalogWithOneStream =
        new ConfiguredAirbyteCatalog().withStreams(List.of(configuredAirbyteStreams.get(0)));

    final List<AirbyteMessage> airbyteMessages = runRead(configuredCatalogWithOneStream, getState());
    final List<AirbyteRecordMessage> recordMessages = filterRecords(airbyteMessages);
    final List<AirbyteStateMessage> stateMessages = airbyteMessages
        .stream()
        .filter(m -> m.getType() == AirbyteMessage.Type.STATE)
        .map(AirbyteMessage::getState)
        .collect(Collectors.toList());
    assertEquals(recordMessages.size(), 1);
    assertFalse(stateMessages.isEmpty(), "Reason");
    ObjectMapper mapper = new ObjectMapper();

    assertEquals(recordMessages.get(0).getData(),
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
    assertEquals(secondSyncRecords.get(0).getData(),
        mapper.readTree("{\"id\":5, \"name\":\"deep space nine\", \"userid\":null}"));

  }

}
