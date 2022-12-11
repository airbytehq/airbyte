/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.tidb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

public class TiDBDestinationTest {

  private GenericContainer container;
  final String SCHEMA_NAME = "public";
  final String STREAM_NAME = "id_and_name";

  @BeforeEach
  public void setup() {
    container = new GenericContainer(DockerImageName.parse("pingcap/tidb:nightly"))
        .withExposedPorts(4000);
    container.start();
  }

  @AfterEach
  public void tearDown() {
    container.stop();
    container.close();
  }

  private JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "127.0.0.1",
        JdbcUtils.PORT_KEY, container.getFirstMappedPort(),
        JdbcUtils.USERNAME_KEY, "root",
        JdbcUtils.DATABASE_KEY, "test"));
  }

  @Test
  public void sanityTest() throws Exception {
    final Destination destination = new TiDBDestination();
    final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            STREAM_NAME,
            SCHEMA_NAME,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING))));
    JsonNode config = getConfig();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, CATALOG, Destination::defaultOutputRecordCollector);
    final List<AirbyteMessage> expectedRecords = getNRecords(10);
    consumer.start();
    expectedRecords.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
    consumer.accept(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(SCHEMA_NAME + "." + STREAM_NAME, 10)))));
    consumer.close();
    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            "",
            DatabaseDriver.MYSQL.getDriverClassName(),
            String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText())));
    final List<JsonNode> actualRecords = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM public._airbyte_raw_id_and_name;"),
        JdbcUtils.getDefaultSourceOperations()::rowToJson);
    final Map<Integer, JsonNode> expectedRecordsWithId = new HashMap<>();
    expectedRecords.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData)
        .forEach(data -> expectedRecordsWithId.put(data.get("id").asInt(), data));
    actualRecords.stream().map(o -> o.get("_airbyte_data").asText()).map(Jsons::deserialize).forEach(actual -> {
      assertTrue(expectedRecordsWithId.containsKey(actual.get("id").asInt()));
      assertEquals(expectedRecordsWithId.get(actual.get("id").asInt()), actual);
    });
  }

  private List<AirbyteMessage> getNRecords(final int n) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(SCHEMA_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());
  }

  @Test
  public void testCheckConnection() throws Exception {
    Destination destination = new TiDBDestination();
    assertEquals(Status.SUCCEEDED, destination.check(getConfig()).getStatus());
  }

}
