/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.time.Instant;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.ClickHouseContainer;

public class ClickhouseDestinationTest {

  private static final String DB_NAME = "default";
  private static final String STREAM_NAME = "id_and_name";
  private static final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private static ClickHouseContainer db;
  private static ConfiguredAirbyteCatalog catalog;
  private static JsonNode config;

  private static final Map<String, String> CONFIG_WITH_SSL = ImmutableMap.of(
      "host", "localhost",
      "port", "1337",
      "username", "user",
      "database", "db");

  private static final Map<String, String> CONFIG_NO_SSL = MoreMaps.merge(
      CONFIG_WITH_SSL,
      ImmutableMap.of(
          "ssl", "false"));

  @BeforeAll
  static void init() {
    db = new ClickHouseContainer("yandex/clickhouse-server");
    db.start();
  }

  @BeforeEach
  void setup() {
    catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            STREAM_NAME,
            DB_NAME,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("name", JsonSchemaType.STRING))));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", DB_NAME)
        .put("ssl", false)
        .build());
  }

  @AfterAll
  static void cleanUp() {
    db.stop();
    db.close();
  }

  @Test
  void testDefaultParamsNoSSL() {
    final Map<String, String> defaultProperties = new ClickhouseDestination().getDefaultConnectionProperties(
        Jsons.jsonNode(CONFIG_NO_SSL));
    assertEquals(new HashMap<>(), defaultProperties);
  }

  @Test
  void testDefaultParamsWithSSL() {
    final Map<String, String> defaultProperties = new ClickhouseDestination().getDefaultConnectionProperties(
        Jsons.jsonNode(CONFIG_WITH_SSL));
    assertEquals(ClickhouseDestination.SSL_JDBC_PARAMETERS, defaultProperties);
  }

  @Test
  void sanityTest() throws Exception {
    final Destination dest = new ClickhouseDestination();
    final AirbyteMessageConsumer consumer = dest.getConsumer(config, catalog,
        Destination::defaultOutputRecordCollector);
    final List<AirbyteMessage> expectedRecords = generateRecords(10);

    consumer.start();
    expectedRecords.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
    consumer.accept(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(ImmutableMap.of(DB_NAME + "." + STREAM_NAME, 10)))));
    consumer.close();

    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.get("password").asText(),
            ClickhouseDestination.DRIVER_CLASS,
            String.format("jdbc:clickhouse://%s:%s/%s",
                config.get("host").asText(),
                config.get("port").asText(),
                config.get("database").asText())
        )
    );

    final List<JsonNode> actualRecords = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery(
            String.format("SELECT * FROM %s.%s;", DB_NAME,
                namingResolver.getRawTableName(STREAM_NAME))),
        JdbcUtils.getDefaultSourceOperations()::rowToJson);

    assertEquals(
        expectedRecords.stream().map(AirbyteMessage::getRecord)
            .map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
        actualRecords.stream()
            .map(o -> o.get("_airbyte_data").asText())
            .map(Jsons::deserialize)
            .sorted(Comparator.comparingInt(x -> x.get("id").asInt()))
            .collect(Collectors.toList()));
  }

  private List<AirbyteMessage> generateRecords(final int n) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(DB_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "test name " + i)))))
        .collect(Collectors.toList());
  }

}
